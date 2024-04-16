define(['summernote/core/range','summernote/core/dom'],function(range,dom){//FLECTRA:suggestupstream
  /**
   *@classediting.History
   *
   *EditorHistory
   *
   */
  varHistory=function($editable){
    varstack=[],stackOffset=-1;
    vareditable=$editable[0];

    varmakeSnapshot=function(){
      varrng=range.create();
      varemptyBookmark={s:{path:[],offset:0},e:{path:[],offset:0}};

      return{
        contents:$editable.html(),
        bookmark:(rng&&dom.ancestor(rng.sc,dom.isEditable)?rng.bookmark(editable):emptyBookmark)
        //FLECTRA:suggestupstreamadded"&&dom.ancestor(rng.sc,dom.isEditable)"
      };
    };

    varapplySnapshot=function(snapshot){
      if(snapshot.contents!==null){
        $editable.html(snapshot.contents);
      }
      if(snapshot.bookmark!==null){
        range.createFromBookmark(editable,snapshot.bookmark).select();
      }
    };

    /**
     *undo
     */
    this.undo=function(){
      //Createsnapshotifnotyetrecorded
      if($editable.html()!==stack[stackOffset].contents){
        this.recordUndo();
      }

      if(0<stackOffset){
        stackOffset--;
        applySnapshot(stack[stackOffset]);
      }
    };

    /*FLECTRA:tosuggestupstream*/
    this.hasUndo=function(){
        return0<stackOffset;
    };

    /**
     *redo
     */
    this.redo=function(){
      if(stack.length-1>stackOffset){
        stackOffset++;
        applySnapshot(stack[stackOffset]);
      }
    };

    /*FLECTRA:tosuggestupstream*/
    this.hasRedo=function(){
        returnstack.length-1>stackOffset;
    };

    varlast;//FLECTRA:tosuggestupstream(sincewemayhaveseveraleditor)
    /**
     *recordedundo
     */
    this.recordUndo=function(){
      //FLECTRA:methodtotallyrewritten
      //testeventforfirefox:removestackofhistorybecauseeventdoesn'texists
      varkey=typeofevent!=='undefined'?event:false;
      if(key&&!event.metaKey&&!event.ctrlKey&&!event.altKey&&event.type==="keydown"){
        key=event.type+"-";
        if(event.which===8||event.which===46)key+='delete';
        elseif(event.which===13)key+='enter';
        elsekey+='other';
        if(key===last)return;
        hasUndo=true;
      }
      last=key;

      //WashoutstackafterstackOffset
      if(stack.length>stackOffset+1){
        stack=stack.slice(0,stackOffset+1);
      }

      if(stack[stackOffset]&&stack[stackOffset].contents===$editable.html()){
        return;
      }

      stackOffset++;

      //Createnewsnapshotandpushittotheend
      stack.push(makeSnapshot());
    };

    /*FLECTRA:tosuggestupstream*/
    this.splitNext=function(){
        last=false;
    };

    /*FLECTRA:tosuggestupstream*/
    this.reset=function(){
        last=false;
        stack=[];
        stackOffset=-1;
        this.recordUndo();
    };

    //Createfirstundostack
    this.recordUndo();
  };

  returnHistory;
});
