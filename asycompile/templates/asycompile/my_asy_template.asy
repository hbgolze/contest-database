
{% autoescape off %}
if(!settings.multipleView) settings.batchView=false;
settings.tex="pdflatex";
defaultfilename="{{filename}}";
if(settings.render < 0) settings.render=4;
settings.outformat="";
settings.inlineimage=true;
settings.embed=true;
settings.toolbar=false;
viewportmargin=(2,2);

{{asy_code}}
{% endautoescape %}
