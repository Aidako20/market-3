flectra.define('point_of_sale.Gui',function(require){
    'usestrict';

    /**
     *Thismodulebridgesthedataclasses(suchasthosedefinedin
     *models.js)totheview(owl.Component)butnotviceversa.
     *
     *Theideaistobeabletoperformside-effectstotheuserinterface
     *duringcalculation.Thinkofconsole.logduringtimeswewanttosee
     *theresultofcalculations.Thisisnodifferent,exceptthatinstead
     *ofprintingsomethingintheconsole,weaccessamethodintheuser
     *interfacethentheuserinterfacereacts,e.g.calling`showPopup`.
     *
     *Thishowevercanbedangeroustotheuserinterfaceasitcanbepossible
     *thatarenderedcomponentisdestroyedduringthecalculation.Becauseof
     *this,wearegoingtolimitexternaluicontrolstothosesafeonesto
     *usesuchas:
     * -`showPopup`
     * -`showTempScreen`
     *
     *IMPROVEMENT:Afterall,thisGuilayerseemstobeagoodabstractionbecause
     *thereisacompletedecouplingbetweendataandviewdespitethedatabeing
     *abletouseselectedfunctionalitiesintheviewlayer.Moreformalized
     *implementationiswelcome.
     */

    constconfig={};

    /**
     *Callthiswhentheuserinterfaceisready.Providethecomponent
     *thatwillbeusedtocontroltheui.
     *@param{owl.component}componentcomponenthavingtheuimethods.
     */
    constconfigureGui=({component})=>{
        config.component=component;
        config.availableMethods=newSet([
            'showPopup',
            'showTempScreen',
            'playSound',
            'setSyncStatus',
        ]);
    };

    /**
     *Importthisandconsumelikeso:`Gui.showPopup(<PopupName>,<props>)`.
     *Likeyouwouldcall`showPopup`inacomponent.
     */
    constGui=newProxy(config,{
        get(target,key){
            const{component,availableMethods}=target;
            if(!component)thrownewError(`Call'configureGui'beforeusingGui.`);
            constisMounted=component.__owl__.status===3/*mounted*/;
            if(availableMethods.has(key)&&isMounted){
                returncomponent[key].bind(component);
            }
        },
    });

    return{configureGui,Gui};
});
