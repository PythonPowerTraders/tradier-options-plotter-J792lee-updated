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

double _d1(double sigma, double S, double K, double r, double q, double t) {
    return (log(S / K) + t * (r - q + (sigma * sigma) * 0.5)) / (sigma * sqrt(t)); 
}

double _d2(double sigma, double S, double K, double r, double q, double t) {
    return _d1(sigma, S, K, r, q, t) - sigma * sqrt(t);
}

double call_price(double sigma, double S, double K, double r, double q, double t, double d1, double d2) {
    return S * exp(-q * t) * _norm_CDF(d1) - K * exp(-r * t) * _norm_CDF(d2);
}

double put_price(double sigma, double S, double K, double r, double q, double t, double d1, double d2) {
    return K * exp(-r * t) * _norm_CDF(-d2) - S * exp(-q * t) * _norm_CDF(-d1);
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

// Price, Underlying, Stike, time to expirey (% of year), risk-free rate (default 0), div-yield (default 0)
static PyObject* getCallVol(PyObject* self, PyObject* args) { 
    double price = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;
    double q = 0.0;

    const double tol = 0.0001;
    double epsilon = 1.0;
    
    int count = 0;
    const int max_iter = 1000;
    
    if (!PyArg_ParseTuple(args, "ddddd|dd", &price, &S, &K, &t, &r, &q))
        return NULL;


    double volGuess = sqrt(2 * M_PI / t) * (price / S);
    double origVol = volGuess;

    while (epsilon > tol) {
        count++;
        if (count >= max_iter) {
            return NULL;
        }

        origVol = volGuess;
        double d1 = _d1(volGuess, S, K, r, q, t);
        double d2 = _d2(volGuess, S, K, r, q, t);
        double fx = call_price(volGuess, S, K, r, q, t, d1, d2) - price;

        double vega = S *  _norm_PDF(d1) * sqrt(t);

        volGuess = -fx / vega + volGuess;

        epsilon = fabs((volGuess - origVol) / origVol);
    }

    return Py_BuildValue("d", volGuess);
}

// Price, Underlying, Stike, time to expirey (% of year), risk-free rate (default 0), div-yield (default 0)
static PyObject* getPutVol(PyObject* self, PyObject* args) { 
    double price = 0.0;
    double S = 0.0;
    double K = 0.0;
    double t = 0.0;
    double r = 0.0;
    double q = 0.0;

    const double tol = 0.0001;
    double epsilon = 1.0;
    
    int count = 0;
    const int max_iter = 1000;
    
    if (!PyArg_ParseTuple(args, "ddddd|dd", &price, &S, &K, &t, &r, &q))
        return NULL;


    double volGuess = sqrt(2 * M_PI / t) * (price / S);
    double origVol = volGuess;

    while (epsilon > tol) {
        count++;
        if (count >= max_iter) {
            return NULL;
        }

        origVol = volGuess;
        double d1 = _d1(volGuess, S, K, r, q, t);
        double d2 = _d2(volGuess, S, K, r, q, t);
        double fx = put_price(volGuess, S, K, r, q, t, d1, d2) - price;

        double vega = S *  _norm_PDF(d1) * sqrt(t);

        volGuess = -fx / vega + volGuess;

        epsilon = fabs((volGuess- origVol) / origVol);
    }

    return Py_BuildValue("d", volGuess);
}

static PyMethodDef OptionMethods[] = {
    {"norm_CDF", norm_CDF, METH_VARARGS, "Calculate the CDF of a normal distribution at a certain value."},
    {"norm_PDF", norm_PDF, METH_VARARGS, "Calculate the PDF of a normal distribution at a certain value."},
    {"getCallVol", getCallVol, METH_VARARGS, "Calculate the volitility of a call option."},
    {"getPutVol", getPutVol, METH_VARARGS, "Calculate the volitility of a put option."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initOptionsPricing(void) {
    (void) Py_InitModule("OptionsPricing", OptionMethods);
}
