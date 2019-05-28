import shogun as sg

def get_kernel(request, features):
    try:
        kernel_name = request.POST["kernel"]
    except:
        raise ValueError("Unknown kernel")
    
    if kernel_name == "GaussianKernel":
        try:
            sigma = float(request.POST["sigma"])
        except:
            raise ValueError("Sigma is not correct")
        kernel = sg.GaussianKernel(features, features, sigma)
    elif kernel_name == "LinearKernel":
        kernel = sg.LinearKernel(features, features)
        kernel.set_normalizer(sg.IdentityKernelNormalizer())
    elif kernel_name == "PolynomialKernel":
        try:
            degree = int(request.POST["degree"])
        except:
            raise ValueError("degree is not correct")
        kernel = sg.PolyKernel(features, features, degree, True)
        kernel.set_normalizer(sg.IdentityKernelNormalizer())
    else:
        raise ValueError("Unknown kernel")
    
    return kernel
