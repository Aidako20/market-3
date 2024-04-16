flectra.define('mail/static/src/component_hooks/use_drag_visible_dropzone/use_drag_visible_dropzone.js',function(require){
'usestrict';

const{useState,onMounted,onWillUnmount}=owl.hooks;

/**
 *Thishookhandlethevisibilityofthedropzonebasedondrag&dropevents.
 *Itneedsareftoadropzone,soyouneedtospecifyat-ref="dropzone"in
 *thetemplateofyourcomponent.
 *
 *@returns{Object}
 */
functionuseDragVisibleDropZone(){
    /**
     *Determinewhetherthedropzoneshouldbevisibleornot.
     *Notethatthisisanobservedvalue,andprimitivetypessuchas
     *booleancannotbeobserved,hencethisisanobjectwithboolean
     *valueaccessiblefrom`.value`
     */
    constisVisible=useState({value:false});

    /**
     *Countshowmanydragenter/leavehappenedglobally.Thisistheonly
     *waytoknowifafilehasbeendraggedoutofthebrowserwindow.
     */
    letdragCount=0;

    //COMPONENTSHOOKS
    onMounted(()=>{
        document.addEventListener('dragenter',_onDragenterListener,true);
        document.addEventListener('dragleave',_onDragleaveListener,true);
        document.addEventListener('drop',_onDropListener,true);

        //ThosesEventspreventthebrowsertoopenordownloadthefileif
        //it'sdroppedoutsideofthedropzone
        window.addEventListener('dragover',ev=>ev.preventDefault());
        window.addEventListener('drop',ev=>ev.preventDefault());
    });

    onWillUnmount(()=>{
        document.removeEventListener('dragenter',_onDragenterListener,true);
        document.removeEventListener('dragleave',_onDragleaveListener,true);
        document.removeEventListener('drop',_onDropListener,true);

        window.removeEventListener('dragover',ev=>ev.preventDefault());
        window.removeEventListener('drop',ev=>ev.preventDefault());
    });

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Showsthedropzonewhenenteringthebrowserwindow,tolettheuserknow
     *wherehecandropitsfile.
     *Avoidschangingstatewhenenteringinnerdropzones.
     *
     *@private
     *@param{DragEvent}ev
     */
    function_onDragenterListener(ev){
        if(
            dragCount===0&&
            ev.dataTransfer&&
            ev.dataTransfer.types.includes('Files')
        ){
            isVisible.value=true;
        }
        dragCount++;
    }

    /**
     *@private
     *@param{DragEvent}ev
     */
    function_onDragleaveListener(ev){
        dragCount--;
        if(dragCount===0){
            isVisible.value=false;
        }
    }

    /**
     *@private
     *@param{DragEvent}ev
     */
    function_onDropListener(ev){
        dragCount=0;
        isVisible.value=false;
    }

    returnisVisible;
}

returnuseDragVisibleDropZone;

});
