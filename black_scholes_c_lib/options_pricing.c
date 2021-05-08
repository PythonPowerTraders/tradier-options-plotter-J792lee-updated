#include <Python.h>
#include <math.h>
#include <stdio.h>

#define M_1_SQRT2PI 0.3989422804014326779399460599343818684758586311649346576659258296

double _norm_CDF(double x) {
    return 0.5 * erfc(-x * M_SQRT1_2);
}

double _norm_PDF(double x) {
    return M_1_SQRT2PI * exp(-(x * x) * 0.5); 
}

double _d1(double sigma, double S, double K, double r, double t) {
    return (log(S / K) + t * (r + (sigma * sigma) * 0.5)) / (sigma * sqrt(t)); 
}

double _d2(double sigma, double S, double K, double r, double t) {
    return _d1(sigma, S, K, r, t) - sigma * sqrt(t);
}

double call_price(double sigma, double S, double K, double r, double t, double d1, double d2) {
    return S * _norm_CDF(d1) - K * exp(-r * t) * _norm_CDF(d2);
}

double put_price(double sigma, double S, double K, double r, double t, double d1, double d2) {
    return K * exp(-r * t) * _norm_CDF(-d2) - S * _norm_CDF(-d1);
}

static PyObject* norm_CDF(PyObject* self, PyObject* args) { // standard normal
    double n;

    if (!PyArg_ParseTuple(args, "d", &n))
        return NULL;

    return Py_BuildValue("d", _norm_CDF(n));
}

static PyObject* norm_PDF(PyObject* self, PyObject* args) { //standard normal
    double n;

    if (!PyArg_ParseTuple(args, "d", &n))
        return NULL;

    return Py_BuildValue("d", _norm_PDF(n));
}

// Price, Underlying, Stike, time to expirey (% of year), risk-free rate (default 0)
static PyObject* getCallVol(PyObject* self, PyObject* args) { 
    double price = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;

    const double tol = 0.0001;
    double epsilon = 1.0;
    
    int count = 0;
    const int max_iter = 1000;
    
    if (!PyArg_ParseTuple(args, "ddddd|d", &price, &S, &K, &t, &r))
        return NULL;


    double volGuess = sqrt(2 * M_PI / t) * (price / S);
    double origVol = volGuess;

    while (epsilon > tol) {
        count++;
        if (count >= max_iter) {
            return NULL;
        }

        origVol = volGuess;
        double d1 = _d1(volGuess, S, K, r, t);
        double d2 = _d2(volGuess, S, K, r, t);
        double fx = call_price(volGuess, S, K, r, t, d1, d2) - price;

        double vega = S *  _norm_PDF(d1) * sqrt(t);

        volGuess = -fx / vega + volGuess;

        epsilon = fabs((volGuess - origVol) / origVol);
    }

    return Py_BuildValue("d", volGuess);
}

// Price, Underlying, Stike, time to expirey (% of year), risk-free rate (default 0)
static PyObject* getPutVol(PyObject* self, PyObject* args) { 
    double price = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;


    const double tol = 0.0001;
    double epsilon = 1.0;
    
    int count = 0;
    const int max_iter = 1000;
    
    if (!PyArg_ParseTuple(args, "ddddd|dd", &price, &S, &K, &t, &r))
        return NULL;


    double volGuess = sqrt(2 * M_PI / t) * (price / S);
    double origVol = volGuess;

    while (epsilon > tol) {
        count++;
        if (count >= max_iter) {
            return NULL;
        }

        origVol = volGuess;
        double d1 = _d1(volGuess, S, K, r, t);
        double d2 = _d2(volGuess, S, K, r, t);
        double fx = put_price(volGuess, S, K, r, t, d1, d2) - price;

        double vega = S *  _norm_PDF(d1) * sqrt(t);

        volGuess = -fx / vega + volGuess;

        epsilon = fabs((volGuess- origVol) / origVol);
    }

    return Py_BuildValue("d", volGuess);
}

static PyObject* getCallDelta(PyObject* self, PyObject* args) { 
    double sigma = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;

    if (!PyArg_ParseTuple(args, "ddddd", &sigma, &S, &K, &t, &r))
        return NULL;

    double d1 = _d1(sigma, S, K, r, t);

    return Py_BuildValue("d", _norm_CDF(d1));
}

static PyObject* getPutDelta(PyObject* self, PyObject* args) { 
    double sigma = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;

    if (!PyArg_ParseTuple(args, "ddddd", &sigma, &S, &K, &t, &r))
        return NULL;

    double d1 = _d1(sigma, S, K, r, t);

    return Py_BuildValue("d", _norm_CDF(d1) - 1);
}

static PyObject* getGamma(PyObject* self, PyObject* args) { 
    double sigma = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;

    if (!PyArg_ParseTuple(args, "ddddd", &sigma, &S, &K, &t, &r))
        return NULL;

    double d1 = _d1(sigma, S, K, r, t);

    return Py_BuildValue("d", _norm_PDF(d1) / (S * sigma * sqrt(t)));
}

static PyObject* getVega(PyObject* self, PyObject* args) { 
    double sigma = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;

    if (!PyArg_ParseTuple(args, "ddddd", &sigma, &S, &K, &t, &r))
        return NULL;

    double d1 = _d1(sigma, S, K, r, t);

    return Py_BuildValue("d", _norm_PDF(d1) * S * sqrt(t));
}

static PyObject* getCallTheta(PyObject* self, PyObject* args) { 
    double sigma = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;

    if (!PyArg_ParseTuple(args, "ddddd", &sigma, &S, &K, &t, &r))
        return NULL;

    double d1 = _d1(sigma, S, K, r, t);
    double d2 = _d2(sigma, S, K, r, t);

    double theta = ((-S * _norm_PDF(d1) * sigma) / (2 * sqrt(t))) - r * K * exp(-r * t) * _norm_CDF(d2);
    return Py_BuildValue("d", theta);
}

static PyObject* getPutTheta(PyObject* self, PyObject* args) { 
    double sigma = 0.0;
    double S = 0.0;
    double K = 0.0;Call

    double d1 = _d1(sigma, S, K, r, t);
    double d2 = _d2(sigma, S, K, r, t);

    double theta = ((-S * _norm_PDF(d1) * sigma) / (2 * sqrt(t))) + r * K * exp(-r * t) * _norm_CDF(-d2);
    return Py_BuildValue("d", theta);
}

static PyObject* getCallRho(PyObject* self, PyObject* args) { 
    double sigma = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;

    if (!PyArg_ParseTuple(args, "ddddd", &sigma, &S, &K, &t, &r))
        return NULL;

    double d2 = _d2(sigma, S, K, r, t);

    double rho = K * t * exp(-r * t) * _norm_CDF(d2);

    return Py_BuildValue("d", rho);
}

static PyObject* getPutRho(PyObject* self, PyObject* args) { 
    double sigma = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;

    if (!PyArg_ParseTuple(args, "ddddd", &sigma, &S, &K, &t, &r))
        return NULL;

    double d2 = _d2(sigma, S, K, r, t);

    double rho = -K * t * exp(-r * t) * _norm_CDF(-d2);
    
    return Py_BuildValue("d", rho);
}

static PyMethodDef OptionMethods[] = {
    {"norm_CDF", norm_CDF, METH_VARARGS, "Calculate the CDF of a normal distribution at a certain value."},
    {"norm_PDF", norm_PDF, METH_VARARGS, "Calculate the PDF of a normal distribution at a certain value."},
    {"getCallVol", getCallVol, METH_VARARGS, "Calculate the volitility of a call option."},
    {"getPutVol", getPutVol, METH_VARARGS, "Calculate the volitility of a put option."},
    {"getCallDelta", getCallDelta, METH_VARARGS, "Calculate the delta of a call option."},
    {"getPutDelta", getPutDelta, METH_VARARGS, "Calculate the delta of a put option."},
    {"getGamma", getGamma, METH_VARARGS, "Calculate the gamma of an option."},
    {"getVega", getVega, METH_VARARGS, "Calculate the vega of an option."},    
    {"getCallTheta", getCallTheta, METH_VARARGS, "Calculate the theta of a call option."},
    {"getPutTheta", getPutTheta, METH_VARARGS, "Calculate the theta of a put option."},
    {"getCallRho", getCallRho, METH_VARARGS, "Calculate the rho of a call option."},
    {"getPutRho", getPutRho, METH_VARARGS, "Calculate the rho of a put option."},
    {NULL, NULL, 0, NULL}
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef cModPyDem =
{
    PyModuleDef_HEAD_INIT,
    "OptionsPricing", "Functions useful for getting volatility of options using Black-Scholes",
    -1,
    OptionMethods
};

PyMODINIT_FUNC PyInit_OptionsPricing(void) {
    return PyModule_Create(&cModPyDem);
}

#else
PyMODINIT_FUNC initOptionsPricing(void) {
    (void) Py_InitModule("OptionsPricing", OptionMethods);
}

#endif