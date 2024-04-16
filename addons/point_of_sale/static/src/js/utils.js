flectra.define('point_of_sale.utils',function(require){
    'usestrict';

    const{EventBus}=owl.core;

    functiongetFileAsText(file){
        returnnewPromise((resolve,reject)=>{
            if(!file){
                reject();
            }else{
                constreader=newFileReader();
                reader.addEventListener('load',function(){
                    resolve(reader.result);
                });
                reader.addEventListener('abort',reject);
                reader.addEventListener('error',reject);
                reader.readAsText(file);
            }
        });
    }

    /**
     *ThisglobalvariableisusedbynextFrametostorethetimerand
     *beabletocancelitbeforeanotherrequestforanimationframe.
     */
    lettimer=null;

    /**
     *Waitforthenextanimationframetofinish.
     */
    constnextFrame=()=>{
        returnnewPromise((resolve)=>{
            cancelAnimationFrame(timer);
            timer=requestAnimationFrame(()=>{
                resolve();
            });
        });
    };

    functionisRpcError(error){
        return(
            !(errorinstanceofError)&&
            error.message&&
            [100,200,404,-32098].includes(error.message.code)
        );
    }

    return{getFileAsText,nextFrame,isRpcError,posbus:newEventBus()};
});
