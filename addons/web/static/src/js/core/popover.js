flectra.define('web.Popover',function(require){
    'usestrict';

    constpatchMixin=require('web.patchMixin');

    const{Component,hooks,misc,QWeb}=owl;
    const{Portal}=misc;
    const{useRef,useState}=hooks;

    /**
     *Popover
     *
     *Representsabootstrap-stylepopoverhandledwithpureJS.Thepopover
     *willbevisuallyboundtoits`target`usinganarrow-like'::before'
     *CSSpseudo-element.
     *@extendsComponent
     **/
    classPopoverextendsComponent{
        /**
         *@param{Object}props
         *@param{String}[props.position='bottom']
         *@param{String}[props.title]
         */
        constructor(){
            super(...arguments);
            this.popoverRef=useRef('popover');
            this.orderedPositions=['top','bottom','left','right'];
            this.state=useState({
                displayed:false,
            });

            this._onClickDocument=this._onClickDocument.bind(this);
            this._onScrollDocument=this._onScrollDocument.bind(this);
            this._onResizeWindow=this._onResizeWindow.bind(this);

            this._onScrollDocument=_.throttle(this._onScrollDocument,50);
            this._onResizeWindow=_.debounce(this._onResizeWindow,250);

            /**
             *Thoseeventsareonlynecessaryifthepopoveriscurrentlyopen,
             *sowedecidedforperformancereasonstoavoidbindingthemwhile
             *itisclosed.Thisallowstohavemanypopoverinstantiatedwhile
             *keepingthecountofglobalhandlerslow.
             */
            this._hasGlobalEventListeners=false;
        }

        mounted(){
            this._compute();
        }

        patched(){
            this._compute();
        }

        willUnmount(){
            if(this._hasGlobalEventListeners){
                this._removeGlobalEventListeners();
            }
        }

        //----------------------------------------------------------------------
        //Private
        //----------------------------------------------------------------------

        /**
         *@private
         */
        _addGlobalEventListeners(){
            /**
             *Usecaptureforthefollowingeventstoensurenootherpartof
             *thecodecanstopitspropagationfromreachinghere.
             */
            document.addEventListener('click',this._onClickDocument,{
                capture:true,
            });
            document.addEventListener('scroll',this._onScrollDocument,{
                capture:true,
            });
            window.addEventListener('resize',this._onResizeWindow);
            this._hasGlobalEventListeners=true;
        }

        _close(){
            this.state.displayed=false;
        }

        /**
         *Computesthepopoveraccordingtoitsprops.Thismethodwilltrytopositionthe
         *popoverasrequested(accordingtothe`position`props).Iftherequestedposition
         *doesnotfittheviewport,otherpositionswillbetriedinaclockwiseorderstarting
         *atherequestedposition(e.g.startingfromleft:top,right,bottom).Ifnoposition
         *isfoundthatfitstheviewport,'bottom'isused.
         *
         *@private
         */
        _compute(){
            if(!this._hasGlobalEventListeners&&this.state.displayed){
                this._addGlobalEventListeners();
            }
            if(this._hasGlobalEventListeners&&!this.state.displayed){
                this._removeGlobalEventListeners();
            }
            if(!this.state.displayed){
                return;
            }

            //copythedefaultorderedpositiontoavoidupdatingtheminplace
            constpossiblePositions=[...this.orderedPositions];
            constpositionIndex=possiblePositions.indexOf(
                this.props.position
            );

            constpositioningData=this.constructor.computePositioningData(
                this.popoverRef.el,
                this.el
            );

            //checkiftherequestedpositionfitstheviewport;ifnot,
            //tryallotherpositionsandfindonethatdoes
            constposition=possiblePositions
                .slice(positionIndex)
                .concat(possiblePositions.slice(0,positionIndex))
                .map((pos)=>positioningData[pos])
                .find((pos)=>{
                    this.popoverRef.el.style.top=`${pos.top}px`;
                    this.popoverRef.el.style.left=`${pos.left}px`;
                    constrect=this.popoverRef.el.getBoundingClientRect();
                    consthtml=document.documentElement;
                    return(
                        rect.top>=0&&
                        rect.left>=0&&
                        rect.bottom<=(window.innerHeight||html.clientHeight)&&
                        rect.right<=(window.innerWidth||html.clientWidth)
                    );
                });

            //removeallexistingpositioningclasses
            possiblePositions.forEach((pos)=>{
                this.popoverRef.el.classList.remove(`o_popover--${pos}`);
            });

            if(position){
                //applythepreferredfoundpositionthatfitstheviewport
                this.popoverRef.el.classList.add(`o_popover--${position.name}`);
            }else{
                //usethegiven`position`propsbecausenopositionfits
                this.popoverRef.el.style.top=`${positioningData[this.props.position].top}px`;
                this.popoverRef.el.style.left=`${positioningData[this.props.position].left}px`;
                this.popoverRef.el.classList.add(`o_popover--${this.props.position}`);
            }
        }

        /**
         *@private
         */
        _removeGlobalEventListeners(){
            document.removeEventListener('click',this._onClickDocument,true);
            document.removeEventListener('scroll',this._onScrollDocument,true);
            window.removeEventListener('resize',this._onResizeWindow);
            this._hasGlobalEventListeners=false;
        }

        //----------------------------------------------------------------------
        //Handlers
        //----------------------------------------------------------------------

        /**
         *Togglesthepopoverdependingonitscurrentstate.
         *
         *@private
         *@param{MouseEvent}ev
         */
        _onClick(ev){
            this.state.displayed=!this.state.displayed;
        }

        /**
         *Aclickoutsidethepopoverwilldismissthecurrentpopover.
         *
         *@private
         *@param{MouseEvent}ev
         */
        _onClickDocument(ev){
            //Handledby`_onClick`.
            if(this.el.contains(ev.target)){
                return;
            }
            //Ignoreclickinsidethepopover.
            if(this.popoverRef.el&&this.popoverRef.el.contains(ev.target)){
                return;
            }
            this._close();
        }

        /**
         *@private
         *@param{Event}ev
         */
        _onPopoverClose(ev){
            this._close();
        }

        /**
         *Popovermustrecomputeitspositionwhenchildrencontentchanges.
         *
         *@private
         *@param{Event}ev
         */
        _onPopoverCompute(ev){
            this._compute();
        }

        /**
         *Aresizeeventwillneedto'reposition'thepopoverclosetoits
         *target.
         *
         *@private
         *@param{Event}ev
         */
        _onResizeWindow(ev){
            if(this.__owl__.status===5/*destroyed*/){
                return;
            }
            this._compute();
        }

        /**
         *Ascrolleventwillneedto'reposition'thepopoverclosetoits
         *target.
         *
         *@private
         *@param{Event}ev
         */
        _onScrollDocument(ev){
            if(this.__owl__.status===5/*destroyed*/){
                return;
            }
            this._compute();
        }

        //----------------------------------------------------------------------
        //Static
        //----------------------------------------------------------------------

        /**
         *Computetheexpectedpositioningcoordinatesforeachpossible
         *positioningbasedonthetargetandpopoversizes.
         *Inparticularthepopovermustnotoverflowtheviewportinany
         *direction,itshouldactuallystayat`margin`distancefromthe
         *bordertolookgood.
         *
         *@static
         *@param{HTMLElement}popoverElementThepopoverelement
         *@param{HTMLElement}targetElementThetargetelement,towhich
         * thepopoverwillbevisually'bound'
         *@param{integer}[margin=16]Minimalacceptedmarginfromtheborder
         * oftheviewport.
         *@returns{Object}
         */
        staticcomputePositioningData(popoverElement,targetElement,margin=16){
            //settargetposition,possibleposition
            constboundingRectangle=targetElement.getBoundingClientRect();
            consttargetTop=boundingRectangle.top;
            consttargetLeft=boundingRectangle.left;
            consttargetHeight=targetElement.offsetHeight;
            consttargetWidth=targetElement.offsetWidth;
            constpopoverHeight=popoverElement.offsetHeight;
            constpopoverWidth=popoverElement.offsetWidth;
            constwindowWidth=window.innerWidth||document.documentElement.clientWidth;
            constwindowHeight=window.innerHeight||document.documentElement.clientHeight;
            constleftOffsetForVertical=Math.max(
                margin,
                Math.min(
                    Math.round(targetLeft-(popoverWidth-targetWidth)/2),
                    windowWidth-popoverWidth-margin,
                ),
            );
            consttopOffsetForHorizontal=Math.max(
                margin,
                Math.min(
                    Math.round(targetTop-(popoverHeight-targetHeight)/2),
                    windowHeight-popoverHeight-margin,
                ),
            );
            return{
                top:{
                    name:'top',
                    top:Math.round(targetTop-popoverHeight),
                    left:leftOffsetForVertical,
                },
                right:{
                    name:'right',
                    top:topOffsetForHorizontal,
                    left:Math.round(targetLeft+targetWidth),
                },
                bottom:{
                    name:'bottom',
                    top:Math.round(targetTop+targetHeight),
                    left:leftOffsetForVertical,
                },
                left:{
                    name:'left',
                    top:topOffsetForHorizontal,
                    left:Math.round(targetLeft-popoverWidth),
                },
            };
        }

    }

    Popover.components={Portal};
    Popover.template='Popover';
    Popover.defaultProps={
        position:'bottom',
    };
    Popover.props={
        position:{
            type:String,
            validate:(p)=>['top','bottom','left','right'].includes(p),
        },
        title:{type:String,optional:true},
    };

    QWeb.registerComponent('Popover',Popover);

    returnpatchMixin(Popover);
});
