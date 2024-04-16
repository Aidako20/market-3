flectra.define('web.daterangepicker.extensions',function(){
'usestrict';

/**
 *Don'tallowusertoselectoffdays(Dateswhichareoutofcurrentcalendar).
 */
varclickDateFunction=daterangepicker.prototype.clickDate;
daterangepicker.prototype.clickDate=function(ev){
    if(!$(ev.target).hasClass('off')){
        clickDateFunction.apply(this,arguments);
    }
};

/**
 *Overridetoopenupordownbasedontop/bottomspaceinwindow.
 */
constmoveFunction=daterangepicker.prototype.move;
daterangepicker.prototype.move=function(){
    constoffset=this.element.offset();
    this.drops=this.container.height()<offset.top?'up':'down';
    moveFunction.apply(this,arguments);
};

});
