flectra.define('web.widget_registry',function(require){
    "usestrict";

    //Thisregistryissupposedtocontainallcustomwidgetsthatwillbe
    //availableinthebasicviews,withthetag<widget/>. Thereare
    //currentlynosuchwidgetinthewebclient,butthefunctionalityis
    //certainlyusefultobeabletocleanlyaddcustombehaviourinbasic
    //views(andmostnotably,theformview)
    //
    //Thewaycustomwidgetsworkisthattheyregisterthemselvestothis
    //registry:
    //
    //widgetRegistry.add('some_name',MyWidget);
    //
    //Then,theyareavailablewiththe<widget/>tag(inthearch):
    //
    //<widgetname="some_name"/>
    //
    //Widgetswillbethenproperlyinstantiated,renderedanddestroyedatthe
    //appropriatetime,withthecurrentstateinsecondargument.
    //
    //Formoreexamples,lookatthetests(grep'<widget'inthetestfolder)

    varRegistry=require('web.Registry');

    returnnewRegistry();
});
