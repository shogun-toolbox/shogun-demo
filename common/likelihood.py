import shogun as sg

def get_likelihood(request):
    try:
        lik_name = request.POST["likelihood"]
    except:
        raise ValueError("Unknown likelihood")
        
    if lik_name == "LogitLikelihood" :
        lik = sg.LogitLikelihood()
    elif lik_name == "ProbitLikelihood" :
        lik = sg.ProbitLikelihood()
    else:
        raise ValueError("Unknown likelihood")
    return lik

