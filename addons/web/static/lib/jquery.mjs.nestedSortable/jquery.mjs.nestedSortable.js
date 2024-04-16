/*
 *jQueryUINestedSortable
 *v2.1a/2016-02-04
 *https://github.com/ilikenwf/nestedSortable
 *
 *Dependson:
 *	jquery.ui.sortable.js1.10+
 *
 *Copyright(c)2010-2016ManueleJSarfattiandcontributors
 *LicensedundertheMITLicense
 *http://www.opensource.org/licenses/mit-license.php
 */
(function(factory){
	"usestrict";

	if(typeofdefine==="function"&&define.amd){

		//AMD.Registerasananonymousmodule.
		define([
			"jquery",
			"jquery-ui/sortable"
		],factory);
	}else{

		//Browserglobals
		factory(window.jQuery);
	}
}(function($){
	"usestrict";

	functionisOverAxis(x,reference,size){
		return(x>reference)&&(x<(reference+size));
	}

	$.widget("mjs.nestedSortable",$.extend({},$.ui.sortable.prototype,{

		options:{
			disableParentChange:false,
			doNotClear:false,
			expandOnHover:700,
			isAllowed:function(){returntrue;},
			isTree:false,
			listType:"ol",
			maxLevels:0,
			protectRoot:false,
			rootID:null,
			rtl:false,
			startCollapsed:false,
			tabSize:20,

			branchClass:"mjs-nestedSortable-branch",
			collapsedClass:"mjs-nestedSortable-collapsed",
			disableNestingClass:"mjs-nestedSortable-no-nesting",
			errorClass:"mjs-nestedSortable-error",
			expandedClass:"mjs-nestedSortable-expanded",
			hoveringClass:"mjs-nestedSortable-hovering",
			leafClass:"mjs-nestedSortable-leaf",
			disabledClass:"mjs-nestedSortable-disabled"
		},

		_create:function(){
			varself=this,
				err;

			this.element.data("ui-sortable",this.element.data("mjs-nestedSortable"));

			//mjs-preventbrowserfromfreezingiftheHTMLisnotcorrect
			if(!this.element.is(this.options.listType)){
				err="nestedSortable:"+
					"PleasecheckthatthelistTypeoptionissettoyouractuallisttype";

				thrownewError(err);
			}

			//ifwehaveatreewithexpanding/collapsingfunctionality,
			//force'intersect'tolerancemethod
			if(this.options.isTree&&this.options.expandOnHover){
				this.options.tolerance="intersect";
			}

			$.ui.sortable.prototype._create.apply(this,arguments);

			//preparethetreebyapplyingtherightclasses
			//(theCSSisresponsibleforactualhide/showfunctionality)
			if(this.options.isTree){
				$(this.items).each(function(){
					var$li=this.item,
						hasCollapsedClass=$li.hasClass(self.options.collapsedClass),
						hasExpandedClass=$li.hasClass(self.options.expandedClass);

					if($li.children(self.options.listType).length){
						$li.addClass(self.options.branchClass);
						//expand/collapseclassonlyiftheyhavechildren

						if(!hasCollapsedClass&&!hasExpandedClass){
							if(self.options.startCollapsed){
								$li.addClass(self.options.collapsedClass);
							}else{
								$li.addClass(self.options.expandedClass);
							}
						}
					}else{
						$li.addClass(self.options.leafClass);
					}
				});
			}
		},

		_destroy:function(){
			this.element
				.removeData("mjs-nestedSortable")
				.removeData("ui-sortable");
			return$.ui.sortable.prototype._destroy.apply(this,arguments);
		},

		_mouseDrag:function(event){
			vari,
				item,
				itemElement,
				intersection,
				self=this,
				o=this.options,
				scrolled=false,
				$document=$(document),
				previousTopOffset,
				parentItem,
				level,
				childLevels,
				itemAfter,
				itemBefore,
				newList,
				method,
				a,
				previousItem,
				nextItem,
				helperIsNotSibling;

			//Computethehelpersposition
			this.position=this._generatePosition(event);
			this.positionAbs=this._convertPositionTo("absolute");

			if(!this.lastPositionAbs){
				this.lastPositionAbs=this.positionAbs;
			}

			//Doscrolling
			if(this.options.scroll){
				if(this.scrollParent[0]!==document&&this.scrollParent[0].tagName!=="HTML"){

					if(
						(
							this.overflowOffset.top+
							this.scrollParent[0].offsetHeight
						)-
						event.pageY<
						o.scrollSensitivity
					){
						scrolled=this.scrollParent.scrollTop()+o.scrollSpeed;
						this.scrollParent.scrollTop(scrolled);
					}elseif(
						event.pageY-
						this.overflowOffset.top<
						o.scrollSensitivity
					){
						scrolled=this.scrollParent.scrollTop()-o.scrollSpeed;
						this.scrollParent.scrollTop(scrolled);
					}

					if(
						(
							this.overflowOffset.left+
							this.scrollParent[0].offsetWidth
						)-
						event.pageX<
						o.scrollSensitivity
					){
						scrolled=this.scrollParent.scrollLeft()+o.scrollSpeed;
						this.scrollParent.scrollLeft(scrolled);
					}elseif(
						event.pageX-
						this.overflowOffset.left<
						o.scrollSensitivity
					){
						scrolled=this.scrollParent.scrollLeft()-o.scrollSpeed;
						this.scrollParent.scrollLeft(scrolled);
					}

				}else{

					if(
						event.pageY-
						$document.scrollTop()<
						o.scrollSensitivity
					){
						scrolled=$document.scrollTop()-o.scrollSpeed;
						$document.scrollTop(scrolled);
					}elseif(
						$(window).height()-
						(
							event.pageY-
							$document.scrollTop()
						)<
						o.scrollSensitivity
					){
						scrolled=$document.scrollTop()+o.scrollSpeed;
						$document.scrollTop(scrolled);
					}

					if(
						event.pageX-
						$document.scrollLeft()<
						o.scrollSensitivity
					){
						scrolled=$document.scrollLeft()-o.scrollSpeed;
						$document.scrollLeft(scrolled);
					}elseif(
						$(window).width()-
						(
							event.pageX-
							$document.scrollLeft()
						)<
						o.scrollSensitivity
					){
						scrolled=$document.scrollLeft()+o.scrollSpeed;
						$document.scrollLeft(scrolled);
					}

				}

				if(scrolled!==false&&$.ui.ddmanager&&!o.dropBehaviour){
					$.ui.ddmanager.prepareOffsets(this,event);
				}
			}

			//Regeneratetheabsolutepositionusedforpositionchecks
			this.positionAbs=this._convertPositionTo("absolute");

			//mjs-findthetopoffsetbeforerearrangement,
			previousTopOffset=this.placeholder.offset().top;

			//Setthehelperposition
			if(!this.options.axis||this.options.axis!=="y"){
				this.helper[0].style.left=this.position.left+"px";
			}
			if(!this.options.axis||this.options.axis!=="x"){
				this.helper[0].style.top=(this.position.top)+"px";
			}

			//mjs-checkandresethoveringstateateachcycle
			this.hovering=this.hovering?this.hovering:null;
			this.mouseentered=this.mouseentered?this.mouseentered:false;

			//mjs-let'sstartcachingsomevariables
			(function(){
				var_parentItem=this.placeholder.parent().parent();
				if(_parentItem&&_parentItem.closest(".ui-sortable").length){
					parentItem=_parentItem;
				}
			}.call(this));

			level=this._getLevel(this.placeholder);
			childLevels=this._getChildLevels(this.helper);
			newList=document.createElement(o.listType);

			//Rearrange
			for(i=this.items.length-1;i>=0;i--){

				//Cachevariablesandintersection,continueifnointersection
				item=this.items[i];
				itemElement=item.item[0];
				intersection=this._intersectsWithPointer(item);
				if(!intersection){
					continue;
				}

				//OnlyputtheplaceholderinsidethecurrentContainer,skipall
				//itemsformothercontainers.Thisworksbecausewhenmoving
				//anitemfromonecontainertoanotherthe
				//currentContainerisswitchedbeforetheplaceholderismoved.
				//
				//Withoutthismovingitemsin"sub-sortables"cancausetheplaceholdertojitter
				//beetweentheouterandinnercontainer.
				if(item.instance!==this.currentContainer){
					continue;
				}

				//Noactionifintersecteditemisdisabled
				//andtheelementaboveorbelowinthedirectionwe'regoingisalsodisabled
				if(itemElement.className.indexOf(o.disabledClass)!==-1){
					//Note:intersectionhardcodeddirectionvaluesfrom
					//jquery.ui.sortable.js:_intersectsWithPointer
					if(intersection===2){
						//Goingdown
						itemAfter=this.items[i+1];
						if(itemAfter&&itemAfter.item.hasClass(o.disabledClass)){
							continue;
						}

					}elseif(intersection===1){
						//Goingup
						itemBefore=this.items[i-1];
						if(itemBefore&&itemBefore.item.hasClass(o.disabledClass)){
							continue;
						}
					}
				}

				method=intersection===1?"next":"prev";

				//cannotintersectwithitself
				//nouselessactionsthathavebeendonebefore
				//noactioniftheitemmovedistheparentoftheitemchecked
				if(itemElement!==this.currentItem[0]&&
					this.placeholder[method]()[0]!==itemElement&&
					!$.contains(this.placeholder[0],itemElement)&&
					(
						this.options.type==="semi-dynamic"?
							!$.contains(this.element[0],itemElement):
							true
					)
				){

					//mjs-weareintersectinganelement:
					//triggerthemouseentereventandstorethisstate
					if(!this.mouseentered){
						$(itemElement).mouseenter();
						this.mouseentered=true;
					}

					//mjs-iftheelementhaschildrenandtheyarehidden,
					//showthemafteradelay(CSSresponsible)
					if(o.isTree&&$(itemElement).hasClass(o.collapsedClass)&&o.expandOnHover){
						if(!this.hovering){
							$(itemElement).addClass(o.hoveringClass);
							this.hovering=window.setTimeout(function(){
								$(itemElement)
									.removeClass(o.collapsedClass)
									.addClass(o.expandedClass);

								self.refreshPositions();
								self._trigger("expand",event,self._uiHash());
							},o.expandOnHover);
						}
					}

					this.direction=intersection===1?"down":"up";

					//mjs-rearrangetheelementsandresettimeoutsandhoveringstate
					if(this.options.tolerance==="pointer"||this._intersectsWithSides(item)){
						$(itemElement).mouseleave();
						this.mouseentered=false;
						$(itemElement).removeClass(o.hoveringClass);
						if(this.hovering){
							window.clearTimeout(this.hovering);
						}
						this.hovering=null;

						//mjs-donotswitchcontainerif
						//it'sarootitemand'protectRoot'istrue
						//orifit'snotarootitembutwearetryingtomakeitroot
						if(o.protectRoot&&
							!(
								this.currentItem[0].parentNode===this.element[0]&&
								//it'sarootitem
								itemElement.parentNode!==this.element[0]
								//it'sintersectinganon-rootitem
							)
						){
							if(this.currentItem[0].parentNode!==this.element[0]&&
								itemElement.parentNode===this.element[0]
							){

								if(!$(itemElement).children(o.listType).length){
									itemElement.appendChild(newList);
									if(o.isTree){
										$(itemElement)
											.removeClass(o.leafClass)
											.addClass(o.branchClass+""+o.expandedClass);
									}
								}

								if(this.direction==="down"){
									a=$(itemElement).prev().children(o.listType);
								}else{
									a=$(itemElement).children(o.listType);
								}

								if(a[0]!==undefined){
									this._rearrange(event,null,a);
								}

							}else{
								this._rearrange(event,item);
							}
						}elseif(!o.protectRoot){
							this._rearrange(event,item);
						}
					}else{
						break;
					}

					//Clearemtpyul's/ol's
					this._clearEmpty(itemElement);

					this._trigger("change",event,this._uiHash());
					break;
				}
			}

			//mjs-tofindtheprevioussiblinginthelist,
			//keepbacktrackinguntilwehitavalidlistitem.
			(function(){
				var_previousItem=this.placeholder.prev();
				if(_previousItem.length){
					previousItem=_previousItem;
				}else{
					previousItem=null;
				}
			}.call(this));

			if(previousItem!=null){
				while(
					previousItem[0].nodeName.toLowerCase()!=="li"||
					previousItem[0].className.indexOf(o.disabledClass)!==-1||
					previousItem[0]===this.currentItem[0]||
					previousItem[0]===this.helper[0]
				){
					if(previousItem[0].previousSibling){
						previousItem=$(previousItem[0].previousSibling);
					}else{
						previousItem=null;
						break;
					}
				}
			}

			//mjs-tofindthenextsiblinginthelist,
			//keepsteppingforwarduntilwehitavalidlistitem.
			(function(){
				var_nextItem=this.placeholder.next();
				if(_nextItem.length){
					nextItem=_nextItem;
				}else{
					nextItem=null;
				}
			}.call(this));

			if(nextItem!=null){
				while(
					nextItem[0].nodeName.toLowerCase()!=="li"||
					nextItem[0].className.indexOf(o.disabledClass)!==-1||
					nextItem[0]===this.currentItem[0]||
					nextItem[0]===this.helper[0]
				){
					if(nextItem[0].nextSibling){
						nextItem=$(nextItem[0].nextSibling);
					}else{
						nextItem=null;
						break;
					}
				}
			}

			this.beyondMaxLevels=0;

			//mjs-iftheitemismovedtotheleft,senditonelevelup
			//butonlyifit'satthebottomofthelist
			if(parentItem!=null&&
				nextItem==null&&
				!(o.protectRoot&&parentItem[0].parentNode==this.element[0])&&
				(
					o.rtl&&
					(
						this.positionAbs.left+
						this.helper.outerWidth()>parentItem.offset().left+
						parentItem.outerWidth()
					)||
					!o.rtl&&(this.positionAbs.left<parentItem.offset().left)
				)
			){

				parentItem.after(this.placeholder[0]);
				helperIsNotSibling=!parentItem
											.children(o.listItem)
											.children("li:visible:not(.ui-sortable-helper)")
											.length;
				if(o.isTree&&helperIsNotSibling){
					parentItem
						.removeClass(this.options.branchClass+""+this.options.expandedClass)
						.addClass(this.options.leafClass);
				}
                if(typeofparentItem!=='undefined')
				   this._clearEmpty(parentItem[0]);
				this._trigger("change",event,this._uiHash());
				//mjs-iftheitemisbelowasiblingandismovedtotheright,
				//makeitachildofthatsibling
			}elseif(previousItem!=null&&
				!previousItem.hasClass(o.disableNestingClass)&&
				(
					previousItem.children(o.listType).length&&
					previousItem.children(o.listType).is(":visible")||
					!previousItem.children(o.listType).length
				)&&
				!(o.protectRoot&&this.currentItem[0].parentNode===this.element[0])&&
				(
					o.rtl&&
					(
						this.positionAbs.left+
						this.helper.outerWidth()<
						previousItem.offset().left+
						previousItem.outerWidth()-
						o.tabSize
					)||
					!o.rtl&&
					(this.positionAbs.left>previousItem.offset().left+o.tabSize)
				)
			){

				this._isAllowed(previousItem,level,level+childLevels+1);

				if(!previousItem.children(o.listType).length){
					previousItem[0].appendChild(newList);
					if(o.isTree){
						previousItem
							.removeClass(o.leafClass)
							.addClass(o.branchClass+""+o.expandedClass);
					}
				}

				//mjs-ifthisitemisbeingmovedfromthetop,addittothetopofthelist.
				if(previousTopOffset&&(previousTopOffset<=previousItem.offset().top)){
					previousItem.children(o.listType).prepend(this.placeholder);
				}else{
					//mjs-otherwise,addittothebottomofthelist.
					previousItem.children(o.listType)[0].appendChild(this.placeholder[0]);
				}
                if(typeofparentItem!=='undefined')
				   this._clearEmpty(parentItem[0]);
				this._trigger("change",event,this._uiHash());
			}else{
				this._isAllowed(parentItem,level,level+childLevels);
			}

			//Posteventstocontainers
			this._contactContainers(event);

			//Interconnectwithdroppables
			if($.ui.ddmanager){
				$.ui.ddmanager.drag(this,event);
			}

			//Callcallbacks
			this._trigger("sort",event,this._uiHash());

			this.lastPositionAbs=this.positionAbs;
			returnfalse;

		},

		_mouseStop:function(event){
			//mjs-iftheitemisinapositionnotallowed,senditback
			if(this.beyondMaxLevels){

				this.placeholder.removeClass(this.options.errorClass);

				if(this.domPosition.prev){
					$(this.domPosition.prev).after(this.placeholder);
				}else{
					$(this.domPosition.parent).prepend(this.placeholder);
				}

				this._trigger("revert",event,this._uiHash());

			}

			//mjs-clearthehoveringtimeout,justtobesure
			$("."+this.options.hoveringClass)
				.mouseleave()
				.removeClass(this.options.hoveringClass);

			this.mouseentered=false;
			if(this.hovering){
				window.clearTimeout(this.hovering);
			}
			this.hovering=null;

			this._relocate_event=event;
			this._pid_current=$(this.domPosition.parent).parent().attr("id");
			this._sort_current=this.domPosition.prev?$(this.domPosition.prev).next().index():0;
			$.ui.sortable.prototype._mouseStop.apply(this,arguments);//asybnchronousexecution,@see_clearfortherelocateevent.
		},

		//mjs-thisfunctionisslightlymodified
		//tomakeiteasiertohoveroveracollapsedelementandhaveitexpand
		_intersectsWithSides:function(item){

			varhalf=this.options.isTree?.8:.5,
				isOverBottomHalf=isOverAxis(
					this.positionAbs.top+this.offset.click.top,
					item.top+(item.height*half),
					item.height
				),
				isOverTopHalf=isOverAxis(
					this.positionAbs.top+this.offset.click.top,
					item.top-(item.height*half),
					item.height
				),
				isOverRightHalf=isOverAxis(
					this.positionAbs.left+this.offset.click.left,
					item.left+(item.width/2),
					item.width
				),
				verticalDirection=this._getDragVerticalDirection(),
				horizontalDirection=this._getDragHorizontalDirection();

			if(this.floating&&horizontalDirection){
				return(
					(horizontalDirection==="right"&&isOverRightHalf)||
					(horizontalDirection==="left"&&!isOverRightHalf)
				);
			}else{
				returnverticalDirection&&(
					(verticalDirection==="down"&&isOverBottomHalf)||
					(verticalDirection==="up"&&isOverTopHalf)
				);
			}

		},

		_contactContainers:function(){

			if(this.options.protectRoot&&this.currentItem[0].parentNode===this.element[0]){
				return;
			}

			$.ui.sortable.prototype._contactContainers.apply(this,arguments);

		},

		_clear:function(){
			vari,
				item;

			$.ui.sortable.prototype._clear.apply(this,arguments);

			//relocateevent
			if(!(this._pid_current===this._uiHash().item.parent().parent().attr("id")&&
				this._sort_current===this._uiHash().item.index())){
				this._trigger("relocate",this._relocate_event,this._uiHash());
			}

			//mjs-cleanlastemptyul/ol
			for(i=this.items.length-1;i>=0;i--){
				item=this.items[i].item[0];
				this._clearEmpty(item);
			}

		},

		serialize:function(options){

			varo=$.extend({},this.options,options),
				items=this._getItemsAsjQuery(o&&o.connected),
				str=[];

			$(items).each(function(){
				varres=($(o.item||this).attr(o.attribute||"id")||"")
						.match(o.expression||(/(.+)[-=_](.+)/)),
					pid=($(o.item||this).parent(o.listType)
						.parent(o.items)
						.attr(o.attribute||"id")||"")
						.match(o.expression||(/(.+)[-=_](.+)/));

				if(res){
					str.push(
						(
							(o.key||res[1])+
							"["+
							(o.key&&o.expression?res[1]:res[2])+"]"
						)+
						"="+
						(pid?(o.key&&o.expression?pid[1]:pid[2]):o.rootID));
				}
			});

			if(!str.length&&o.key){
				str.push(o.key+"=");
			}

			returnstr.join("&");

		},

		toHierarchy:function(options){

			varo=$.extend({},this.options,options),
				ret=[];

			$(this.element).children(o.items).each(function(){
				varlevel=_recursiveItems(this);
				ret.push(level);
			});

			returnret;

			function_recursiveItems(item){
				varid=($(item).attr(o.attribute||"id")||"").match(o.expression||(/(.+)[-=_](.+)/)),
					currentItem;

				vardata=$(item).data();
				if(data.nestedSortableItem){
					deletedata.nestedSortableItem;//RemovethenestedSortableItemobjectfromthedata
				}

				if(id){
					currentItem={
						"id":id[2]
					};

					currentItem=$.extend({},currentItem,data);//Combinethetwoobjects

					if($(item).children(o.listType).children(o.items).length>0){
						currentItem.children=[];
						$(item).children(o.listType).children(o.items).each(function(){
							varlevel=_recursiveItems(this);
							currentItem.children.push(level);
						});
					}
					returncurrentItem;
				}
			}
		},

		toArray:function(options){

			varo=$.extend({},this.options,options),
				sDepth=o.startDepthCount||0,
				ret=[],
				left=1;

			if(!o.excludeRoot){
				ret.push({
					"item_id":o.rootID,
					"parent_id":null,
					"depth":sDepth,
					"left":left,
					"right":($(o.items,this.element).length+1)*2
				});
				left++;
			}

			$(this.element).children(o.items).each(function(){
				left=_recursiveArray(this,sDepth,left);
			});

			ret=ret.sort(function(a,b){return(a.left-b.left);});

			returnret;

			function_recursiveArray(item,depth,_left){

				varright=_left+1,
					id,
					pid,
					parentItem;

				if($(item).children(o.listType).children(o.items).length>0){
					depth++;
					$(item).children(o.listType).children(o.items).each(function(){
						right=_recursiveArray($(this),depth,right);
					});
					depth--;
				}

				id=($(item).attr(o.attribute||"id")).match(o.expression||(/(.+)[-=_](.+)/));

				if(depth===sDepth){
					pid=o.rootID;
				}else{
					parentItem=($(item).parent(o.listType)
											.parent(o.items)
											.attr(o.attribute||"id"))
											.match(o.expression||(/(.+)[-=_](.+)/));
					pid=parentItem[2];
				}

				if(id){
					vardata=$(item).children('div').data();
					varitemObj=$.extend(data,{
						"id":id[2],
						"parent_id":pid,
						"depth":depth,
						"left":_left,
						"right":right
						});
					ret.push(itemObj);
				}

				_left=right+1;
				return_left;
			}

		},

		_clearEmpty:function(item){
			functionreplaceClass(elem,search,replace,swap){
				if(swap){
					search=[replace,replace=search][0];
				}

				$(elem).removeClass(search).addClass(replace);
			}

			varo=this.options,
				childrenList=$(item).children(o.listType),
				hasChildren=childrenList.has('li').length;

			vardoNotClear=
				o.doNotClear||
				hasChildren||
				o.protectRoot&&$(item)[0]===this.element[0];

			if(o.isTree){
				replaceClass(item,o.branchClass,o.leafClass,doNotClear);
			}

			if(!doNotClear){
				childrenList.parent().removeClass(o.expandedClass);
				childrenList.remove();
			}
		},

		_getLevel:function(item){

			varlevel=1,
				list;

			if(this.options.listType){
				list=item.closest(this.options.listType);
				while(list&&list.length>0&&!list.is(".ui-sortable")){
					level++;
					list=list.parent().closest(this.options.listType);
				}
			}

			returnlevel;
		},

		_getChildLevels:function(parent,depth){
			varself=this,
				o=this.options,
				result=0;
			depth=depth||0;

			$(parent).children(o.listType).children(o.items).each(function(index,child){
				result=Math.max(self._getChildLevels(child,depth+1),result);
			});

			returndepth?result+1:result;
		},

		_isAllowed:function(parentItem,level,levels){
			varo=this.options,
				//thistakesintoaccountthemaxLevelssettotherecipientlist
				maxLevels=this
					.placeholder
					.closest(".ui-sortable")
					.nestedSortable("option","maxLevels"),

				//Checkiftheparenthaschangedtopreventit,wheno.disableParentChangeistrue
				oldParent=this.currentItem.parent().parent(),
				disabledByParentchange=o.disableParentChange&&(
					//Fromsomewheretosomewhereelse,excepttheroot
					typeofparentItem!=='undefined'&&!oldParent.is(parentItem)||
					typeofparentItem==='undefined'&&oldParent.is("li")	//Fromsomewheretotheroot
				);
			//mjs-istherootprotected?
			//mjs-arewenestingtoodeep?
			if(
				disabledByParentchange||
				!o.isAllowed(this.placeholder,parentItem,this.currentItem)
			){
				this.placeholder.addClass(o.errorClass);
				if(maxLevels<levels&&maxLevels!==0){
					this.beyondMaxLevels=levels-maxLevels;
				}else{
					this.beyondMaxLevels=1;
				}
			}else{
				if(maxLevels<levels&&maxLevels!==0){
					this.placeholder.addClass(o.errorClass);
					this.beyondMaxLevels=levels-maxLevels;
				}else{
					this.placeholder.removeClass(o.errorClass);
					this.beyondMaxLevels=0;
				}
			}
		}

	}));

	$.mjs.nestedSortable.prototype.options=$.extend(
		{},
		$.ui.sortable.prototype.options,
		$.mjs.nestedSortable.prototype.options
	);
}));