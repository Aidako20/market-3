/*
 *jQueryHotkeysPlugin
 *Copyright2010,JohnResig
 *DuallicensedundertheMITorGPLVersion2licenses.
 *
 *BaseduponthepluginbyTzuryBarYochay:
 *http://github.com/tzuryby/hotkeys
 *
 *Originalideaby:
 *BinnyVA,http://www.openjs.com/scripts/events/keyboard_shortcuts/
*/

(function(jQuery){
	
	jQuery.hotkeys={
		version:"0.8",

		specialKeys:{
			8:"backspace",9:"tab",13:"return",16:"shift",17:"ctrl",18:"alt",19:"pause",
			20:"capslock",27:"esc",32:"space",33:"pageup",34:"pagedown",35:"end",36:"home",
			37:"left",38:"up",39:"right",40:"down",45:"insert",46:"del",
			96:"0",97:"1",98:"2",99:"3",100:"4",101:"5",102:"6",103:"7",
			104:"8",105:"9",106:"*",107:"+",109:"-",110:".",111:"/",
			112:"f1",113:"f2",114:"f3",115:"f4",116:"f5",117:"f6",118:"f7",119:"f8",
			120:"f9",121:"f10",122:"f11",123:"f12",144:"numlock",145:"scroll",191:"/",224:"meta"
		},
	
		shiftNums:{
			"`":"~","1":"!","2":"@","3":"#","4":"$","5":"%","6":"^","7":"&",
			"8":"*","9":"(","0":")","-":"_","=":"+",";":":","'":"\"",",":"<",
			".":">", "/":"?", "\\":"|"
		}
	};

	functionkeyHandler(handleObj){
		//Onlycarewhenapossibleinputhasbeenspecified
		if(typeofhandleObj.data!=="string"){
			return;
		}
		
		varorigHandler=handleObj.handler,
			keys=handleObj.data.toLowerCase().split("");
	
		handleObj.handler=function(event){
			//Don'tfireintext-acceptinginputsthatwedidn'tdirectlybindto
			if(this!==event.target&&(/textarea|select/i.test(event.target.nodeName)||
				event.target.type==="text")){
				return;
			}
			
			//Keypressrepresentscharacters,notspecialkeys
			varspecial=event.type!=="keypress"&&jQuery.hotkeys.specialKeys[event.which],
				character=String.fromCharCode(event.which).toLowerCase(),
				key,modif="",possible={};

			//checkcombinations(alt|ctrl|shift+anything)
			if(event.altKey&&special!=="alt"){
				modif+="alt+";
			}

			if(event.ctrlKey&&special!=="ctrl"){
				modif+="ctrl+";
			}
			
			//TODO:Needtomakesurethisworksconsistentlyacrossplatforms
			if(event.metaKey&&!event.ctrlKey&&special!=="meta"){
				modif+="meta+";
			}

			if(event.shiftKey&&special!=="shift"){
				modif+="shift+";
			}

			if(special){
				possible[modif+special]=true;

			}else{
				possible[modif+character]=true;
				possible[modif+jQuery.hotkeys.shiftNums[character]]=true;

				//"$"canbetriggeredas"Shift+4"or"Shift+$"orjust"$"
				if(modif==="shift+"){
					possible[jQuery.hotkeys.shiftNums[character]]=true;
				}
			}

			for(vari=0,l=keys.length;i<l;i++){
				if(possible[keys[i]]){
					returnorigHandler.apply(this,arguments);
				}
			}
		};
	}

	jQuery.each(["keydown","keyup","keypress"],function(){
		jQuery.event.special[this]={add:keyHandler};
	});

})(jQuery);