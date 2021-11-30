from django.shortcuts import render

def analysis(requests):
    return render(requests, "gcampusanalysis/analysis.html")

def analysis_measurement(requests):
    return render(requests, "gcampusanalysis/analysis_measurement.html")
