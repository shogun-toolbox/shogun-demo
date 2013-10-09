from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
import os
import asp
import json
import sys
import bz2
import StringIO
import genomic

def handler(request):
    if request.method == 'GET':
        return _entrance(request)
    else:
        return _asp(request)

arguments = [
    {
        'argument_type': 'select',
        'argument_name': 'strand',
        'argument_items': ['+', '-' ],
        'argument_default': '+',
    },
    {
        'argument_type': 'select',
        'argument_name': 'organism',
        'argument_items': ['Worm', 'Cress', 'Fish', 'Fly', 'Human'],
        'argument_default': 'Worm',
        'argument_explain': 'asp model for organism when predicting <br/>(one of Cress, Fish, Fly, Human, Worm)'
    },
    {
        'argument_type': 'decimal',
        'argument_name': 'start',
        'argument_default': 499,
        'argument_explain': 'coding start (zero based, relative to sequence start)'
    },
    {
        'argument_type': 'decimal',
        'argument_name': 'stop',
        'argument_default': -499,
        'argument_explain': 'coding stop (zero based, if positive relative to<br/>sequence start, if negative relative to sequence end)'
    },
    {
        'argument_type': 'select',
        'argument_name': 'feature',
        'argument_items': ['acceptor', 'donor'],
        'argument_default': 'acceptor',
    },
    {
        'argument_type': 'ascii_file',
        'argument_name': 'sequence',
    },
    {
        'argument_type': 'button-group',
        'argument_items': [{'button_name': 'run'},
                           {'button_name': 'clear'}],
    }
]


properties = { 'title': 'ASP',
               'template': {'type': 'coordinate-2dims',
                            'feature': 'binary',
                            'coordinate_range': {'horizontal': [0, 1],
                                                 'vertical': [0, 0.8]},
                            'coordinate_system': {'horizontal_axis': {'position': 'bottom',
                                                                      'label': 'X-axis',
                                                                      'range': [0, 1]},
                                                  'vertical_axis': {'position': 'left',
                                                                    'label': 'Y-axis',
                                                                    'range': [0, 1]}},
                            'mouse_click_enabled': 'none'},
                'panels': [
                    {
                        'panel_name': 'arguments',
                        'panel_label': 'Dashboard',
                        'panel_property': arguments,
                    }, ]}

def _entrance(request):
    return render_to_response("application/asp.html",
                              properties,
                              context_instance=RequestContext(request))
def _asp(request):
    try:
        organism = str(request.POST['organism'])
        sequence = str(request.POST['sequence'])
        start = int(request.POST['start'])
        stop = int(request.POST['stop'])
        strand = str(request.POST['strand'])
        feature = str(request.POST['feature'])

        if strand == '-':
            strand = '-'
        else:
            strand = '+'

        modelfname = 'data/asp/%s.dat.bz2' % organism

        # length limit to no smaller than 10 byte and no bigger than 2M
        if len(sequence) <= 10 or len(sequence) > 2*1024*1024:
            raise ValueError("fasta file incorrect")

        if not os.path.isfile(modelfname):
            raise ValueError("model should be one of Cress, Fish, Fly, Human, Worm")

        if start<80:
            raise ValueError("--start value must be >=80")

        if stop > 0 and start >= stop - 80:
            raise ValueError("--stop value must be > start + 80")

        if stop < 0 and stop > -80:
            raise ValueError("--stop value must be <= - 80")

        # shift the start and stop a bit
        start -= 1
        stop -= 1
        sequence_buf = StringIO.StringIO()
        sequence_buf.write(sequence)
        sequence_buf.seek(0)

        fasta_dict = genomic.read_fasta(sequence_buf)
        a = asp.asp()
        a.load_model(modelfname)

        (acc_result, don_result) = _predict(a, sequence_buf, (start,stop), strand)
        if feature == 'donor':
            return HttpResponse(json.dumps(don_result))
        else:
            return HttpResponse(json.dumps(acc_result))

    except ValueError as e:
        return HttpResponse(json.dumps({"status": e.message}))
    except:
        import traceback
        return HttpResponse(json.dumps({"status": repr(traceback.format_exc())}))
def _predict(asp, sequence_buf, (start,end), strand):
    skipheader = False
    sequence_buf.seek(0)
    fasta_dict = genomic.read_fasta(sequence_buf)

    if strand == '-':
        for k, kseq in fasta_dict.ordered_items():
            fasta_dict[k]=genomic.reverse_complement(kseq)

    import seqdict
    seqs = seqdict.seqdict(fasta_dict, (start, end))

    asp.signal.predict_acceptor_sites_from_seqdict(seqs)
    asp.signal.predict_donor_sites_from_seqdict(seqs)

    contig_no = 0;
    for seq in seqs:
        contig_no = contig_no + 1
        l = len(seq.preds['donor'].get_positions())
        p = [i+1 for i in seq.preds['donor'].get_positions()]
        s = seq.preds['donor'].get_scores()
        f = []
        for pos in p:
            if seq.seq[pos-1:pos+1] == 'GT':
                f.append(('GT'))
            else:
                f.append(('GC'))
                assert(seq.seq[pos-1:pos+1] == 'GC')

        if strand == '-':
            p = p[len(p)::-1]
            p = [len(seq.seq)-i for i in p]
            s = s[len(s)::-1]
            f = f[len(f)::-1]

        don_preds = (f, p, s)

        l = len(seq.preds['acceptor'].get_positions())
        p = [i-1 for i in seq.preds['acceptor'].get_positions()]
        s = seq.preds['acceptor'].get_scores()
        f = l*['AG']

        if strand == '-':
            p = p[len(p)::-1]
            p = [len(seq.seq)-i for i in p]
            s = s[len(s)::-1]
            f = f[len(f)::-1]

        acc_preds = (f, p ,s)

        acc_result = []
        don_result = []

        # acc
        for i in xrange(len(acc_preds[0])):
            d = dict()
            if strand == '+':
                d['x'] = acc_preds[1][i]+2
            else:
                d['x'] = acc_preds[1][i]-1
            d['y'] = asp.sigmoid_transform(acc_preds[2][i])
            acc_result.append(d)

        #don
        for i in xrange(len(don_preds[0])):
            d = dict()
            if strand == '+':
                d['x'] = don_preds[1][i]
            else:
                d['x'] = don_preds[1][i]+1
            d['y'] = asp.sigmoid_transform(don_preds[2][i])
            don_result.append(d)
        return (acc_result, don_result)
