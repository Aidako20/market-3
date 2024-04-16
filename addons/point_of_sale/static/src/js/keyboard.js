flectra.define('point_of_sale.keyboard',function(require){
"usestrict";

varWidget=require('web.Widget');

//----------OnScreenKeyboardWidget----------
//AWidgetthatdisplaysanonscreenkeyboard.
//Therearetwooptionswhencreatingthewidget:
//
//*'keyboard_model':'simple'(default)|'full'
//  The'full'emulatesaPCkeyboard,while'simple'emulatesan'android'one.
//
//*'input_selector :(default:'.searchboxinput')
//  definesthedomelementthatthekeyboardwillwriteto.
//
//Thewidgetisinitiallyhidden.Itcanbeshownwiththis.show(),andis
//automaticallyshownwhentheinput_selectorgetsfocused.

varOnscreenKeyboardWidget=Widget.extend({
    template:'OnscreenKeyboardSimple',
    init:function(parent,options){
        this._super(parent,options);
        options=options||{};

        this.keyboard_model=options.keyboard_model||'simple';
        if(this.keyboard_model==='full'){
            this.template='OnscreenKeyboardFull';
        }

        this.input_selector=options.input_selector||'.searchboxinput';
        this.$target=null;

        //Keyboardstate
        this.capslock=false;
        this.shift   =false;
        this.numlock =false;
    },
    
    connect:function(target){
        varself=this;
        this.$target=$(target);
        this.$target.focus(function(){self.show();});
    },
    generateEvent:function(type,key){
        varevent=document.createEvent("KeyboardEvent");
        varinitMethod= event.initKeyboardEvent?'initKeyboardEvent':'initKeyEvent';
        event[initMethod]( type,
                            true,//bubbles
                            true,//cancelable
                            window,//viewArg
                            false,//ctrl
                            false,//alt
                            false,//shift
                            false,//meta
                            ((typeofkey.code==='undefined')?key.char.charCodeAt(0):key.code),
                            ((typeofkey.char==='undefined')?String.fromCharCode(key.code):key.char)
                        );
        returnevent;

    },

    //Writeacharactertotheinputzone
    writeCharacter:function(character){
        varinput=this.$target[0];
        input.dispatchEvent(this.generateEvent('keypress',{char:character}));
        if(character!=='\n'){
            input.value+=character;
        }
        input.dispatchEvent(this.generateEvent('keyup',{char:character}));
    },
    
    //Removesthelastcharacterfromtheinputzone.
    deleteCharacter:function(){
        varinput=this.$target[0];
        input.dispatchEvent(this.generateEvent('keypress',{code:8}));
        input.value=input.value.substr(0,input.value.length-1);
        input.dispatchEvent(this.generateEvent('keyup',{code:8}));
    },
    
    //Clearsthecontentoftheinputzone.
    deleteAllCharacters:function(){
        varinput=this.$target[0];
        if(input.value){
            input.dispatchEvent(this.generateEvent('keypress',{code:8}));
            input.value="";
            input.dispatchEvent(this.generateEvent('keyup',{code:8}));
        }
    },

    //Makesthekeyboardshowandslidefromthebottomofthescreen.
    show: function(){
        $('.keyboard_frame').show().css({'height':'235px'});
    },
    
    //Makesthekeyboardhidebyslidingtothebottomofthescreen.
    hide: function(){
        $('.keyboard_frame')
            .css({'height':'0'})
            .hide();
        this.reset();
    },
    
    //Whathappenswhentheshiftkeyispressed:togglecase,removecapslock
    toggleShift:function(){
        $('.letter').toggleClass('uppercase');
        $('.symbolspan').toggle();
        
        this.shift=(this.shift===true)?false:true;
        this.capslock=false;
    },
    
    //whathappenswhencapslockispressed:togglecase,setcapslock
    toggleCapsLock:function(){
        $('.letter').toggleClass('uppercase');
        this.capslock=true;
    },
    
    //Whathappenswhennumlockispressed:togglesymbolsandnumlocklabel
    toggleNumLock:function(){
        $('.symbolspan').toggle();
        $('.numlockspan').toggle();
        this.numlock=(this.numlock===true)?false:true;
    },

    //Afterakeyispressed,shiftisdisabled.
    removeShift:function(){
        if(this.shift===true){
            $('.symbolspan').toggle();
            if(this.capslock===false)$('.letter').toggleClass('uppercase');
            
            this.shift=false;
        }
    },

    //Resetsthekeyboardtoitsoriginalstate;capslock:false,shift:false,numlock:false
    reset:function(){
        if(this.shift){
            this.toggleShift();
        }
        if(this.capslock){
            this.toggleCapsLock();
        }
        if(this.numlock){
            this.toggleNumLock();
        }
    },

    //calledafterthekeyboardisintheDOM,setsupthekeybindings.
    start:function(){
        varself=this;

        //this.show();


        $('.close_button').click(function(){
            self.deleteAllCharacters();
            self.hide();
        });

        //Keyboardkeyclickhandling
        $('.keyboardli').click(function(){
            
            var$this=$(this),
                character=$this.html();//Ifit'salowercaseletter,nothinghappenstothisvariable
            
            if($this.hasClass('left-shift')||$this.hasClass('right-shift')){
                self.toggleShift();
                returnfalse;
            }
            
            if($this.hasClass('capslock')){
                self.toggleCapsLock();
                returnfalse;
            }
            
            if($this.hasClass('delete')){
                self.deleteCharacter();
                returnfalse;
            }

            if($this.hasClass('numlock')){
                self.toggleNumLock();
                returnfalse;
            }
            
            //Specialcharacters
            if($this.hasClass('symbol'))character=$('span:visible',$this).html();
            if($this.hasClass('space'))character='';
            if($this.hasClass('tab'))character="\t";
            if($this.hasClass('return'))character="\n";
            
            //Uppercaseletter
            if($this.hasClass('uppercase'))character=character.toUpperCase();
            
            //Removeshiftonceakeyisclicked.
            self.removeShift();

            self.writeCharacter(character);
        });
    },
});

return{
    OnscreenKeyboardWidget:OnscreenKeyboardWidget,
};

});
