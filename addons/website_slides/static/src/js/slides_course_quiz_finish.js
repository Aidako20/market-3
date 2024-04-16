flectra.define('website_slides.quiz.finish',function(require){
'usestrict';

varDialog=require('web.Dialog');
varcore=require('web.core');
var_t=core._t;

/**
 *Thismodalisusedwhentheuserfinishesthequiz.
 *Ithandlestheanimationofkarmagainandlevelingupbyanimating
 *theprogressbarandthetext.
 */
varSlideQuizFinishModal=Dialog.extend({
    template:'slide.slide.quiz.finish',
    events:{
        "click.o_wslides_quiz_modal_btn":'_onClickNext',
    },

    init:function(parent,options){
        varself=this;
        this.quiz=options.quiz;
        this.hasNext=options.hasNext;
        this.userId=options.userId;
        options=_.defaults(options||{},{
            size:'medium',
            dialogClass:'d-flexp-0',
            technical:false,
            renderHeader:false,
            renderFooter:false
        });
        this._super.apply(this,arguments);
        this.opened(function(){
            self._animateProgressBar();
            self._animateText();
        })
    },

    start:function(){
        varself=this;
        this._super.apply(this,arguments).then(function(){
            self.$modal.addClass('o_wslides_quiz_modalpt-5');
            self.$modal.find('.modal-dialog').addClass('mt-5');
            self.$modal.find('.modal-content').addClass('shadow-lg');
        });
    },

    //--------------------------------
    //Handlers
    //--------------------------------

    _onClickNext:function(){
        this.trigger_up('slide_go_next');
        this.destroy();
    },

    //--------------------------------
    //Private
    //--------------------------------

    /**
     *Handlestheanimationofthekarmagaininthefollowingsteps:
     *1.InitiatethetooltipwhichwilldisplaytheactualKarma
     *   overtheprogressbar.
     *2.Animatethetooltiptexttoincrementsmoothlyfromtheold
     *   karmavaluetothenewkarmavalueandupdatesittomakeit
     *   moveastheprogressbarmoves.
     *3a.Theuserdoesn'tlevelup
     *   I.  Whentheuserdoesn'tleveluptheprogressbarsimplygoes
     *        fromtheoldkarmavaluetothenewkarmavalue.
     *3b.Theuserlevelsup
     *   I.  Thefirststepmakestheprogressbargofromtheoldkarma
     *        valueto100%.
     *   II. Thesecondstepmakestheprogressbargofrom100%to0%.
     *   III.Thethirdandfinalstepmakestheprogressbargofrom0%
     *        tothenewkarmavalue.Italsochangesthelowerandupper
     *        boundtomatchthenewrank.
     *@param$modal
     *@paramrankProgress
     *@private
     */
    _animateProgressBar:function(){
        varself=this;
        this.$('[data-toggle="tooltip"]').tooltip({
            trigger:'manual',
            container:'.progress-bar-tooltip',
        }).tooltip('show');

        this.$('.tooltip-inner')
            .prop('karma',this.quiz.rankProgress.previous_rank.karma)
            .animate({
                karma:this.quiz.rankProgress.new_rank.karma
            },{
                duration:this.quiz.rankProgress.level_up?1700:800,
                step:function(newKarma){
                    self.$('.tooltip-inner').text(Math.ceil(newKarma));
                    self.$('[data-toggle="tooltip"]').tooltip('update');
                }
            }
        );

        var$progressBar=this.$('.progress-bar');
        if(this.quiz.rankProgress.level_up){
            this.$('.o_wslides_quiz_modal_title').text(_t('Levelup!'));
            $progressBar.css('width','100%');
            _.delay(function(){
                self.$('.o_wslides_quiz_modal_rank_lower_bound')
                    .text(self.quiz.rankProgress.new_rank.lower_bound);
                self.$('.o_wslides_quiz_modal_rank_upper_bound')
                    .text(self.quiz.rankProgress.new_rank.upper_bound||"");

                //weneedtouse_.delaytoforceDOMre-renderingbetween0andnewpercentage
                _.delay(function(){
                    $progressBar.addClass('no-transition').width('0%');
                },1);
                _.delay(function(){
                    $progressBar
                        .removeClass('no-transition')
                        .width(self.quiz.rankProgress.new_rank.progress+'%');
                },100);
            },800);
        }else{
            $progressBar.css('width',this.quiz.rankProgress.new_rank.progress+'%');
        }
    },

    /**
     *Handlestheanimationofthedifferenttextsuchasthekarmagain
     *andthemotivationalmessagewhentheuserlevelsup.
     *@private
     */
    _animateText:function(){
        varself=this;
       _.delay(function(){
            self.$('h4.o_wslides_quiz_modal_xp_gained').addClass('showin');
            self.$('.o_wslides_quiz_modal_dismiss').removeClass('d-none');
        },800);

        if(this.quiz.rankProgress.level_up){
            _.delay(function(){
                self.$('.o_wslides_quiz_modal_rank_motivational').addClass('fade');
                _.delay(function(){
                    self.$('.o_wslides_quiz_modal_rank_motivational').html(
                        self.quiz.rankProgress.last_rank?
                            self.quiz.rankProgress.description:
                            self.quiz.rankProgress.new_rank.motivational
                    );
                    self.$('.o_wslides_quiz_modal_rank_motivational').addClass('showin');
                },800);
            },800);
        }
    },

});

returnSlideQuizFinishModal;

});
