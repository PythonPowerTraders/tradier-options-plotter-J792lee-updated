#include <Python.h>
#include <math.h>
#include <stdio.h>

double _norm_CDF(double x) {
    return 0.5 * erfc(-x * M_SQRT1_2);
}

double d1(double sigma, double S, double K, double r, double q, double t) {
    return log(S / K) + t * (r - q + (sigma * sigma) * 0.5) / (sigma * sqrt(t)); 
}

double d2(double sigma, double S, double K, double r, double q, double t) {
    return d1(sigma, S, K, r, q, t) - sigma * sqrt(t);
}

double call_price() {

}

double put_price() {
    
    
}
static PyObject* norm_CDF(PyObject* self, PyObject* args) {
    double n;

    if (!PyArg_ParseTuple(args, "d", &n))
        return NULL;

    return Py_BuildValue("d", _norm_CDF(n));
}

static PyObject* hello(PyObject* self, PyObject* args) {
    double n;

    if (!PyArg_ParseTuple(args, "d", &n))
        return NULL;

    printf("test");
    Py_RETURN_NONE;
}

static PyMethodDef OptionMethods[] = {
    {"norm_CDF", norm_CDF, METH_VARARGS, "Calculate the CDF of a normal distribution at a certain value."},
    {"hello", hello, METH_VARARGS, "Greet somebody."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initOptionsPricing(void) {
    (void) Py_InitModule("OptionsPricing", OptionMethods);
}
