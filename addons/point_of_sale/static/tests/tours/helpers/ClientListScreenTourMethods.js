flectra.define('point_of_sale.tour.ClientListScreenTourMethods',function(require){
    'usestrict';

    const{createTourMethods}=require('point_of_sale.tour.utils');

    classDo{
        clickClient(name){
            return[
                {
                    content:`clickclient'${name}'fromclientlistscreen`,
                    trigger:`.clientlist-screen.client-list-contents.client-linetd:contains("${name}")`,
                },
                {
                    content:`checkifclient'${name}'ishighlighted`,
                    trigger:`.clientlist-screen.client-list-contents.client-line.highlighttd:contains("${name}")`,
                    run:()=>{},
                },
            ];
        }
        clickSet(){
            return[
                {
                    content:'checkifsetbuttonshown',
                    trigger:'.clientlist-screen.button.next.highlight',
                    run:()=>{},
                },
                {
                    content:'clicksetbutton',
                    trigger:'.clientlist-screen.button.next.highlight',
                },
            ];
        }
    }

    classCheck{
        isShown(){
            return[
                {
                    content:'clientlistscreenisshown',
                    trigger:'.pos-content.clientlist-screen',
                    run:()=>{},
                },
            ];
        }
    }

    classExecute{
        setClient(name){
            conststeps=[];
            steps.push(...this._do.clickClient(name));
            steps.push(...this._do.clickSet());
            returnsteps;
        }
    }

    returncreateTourMethods('ClientListScreen',Do,Check,Execute);
});
