
/* Merged Plone Javascript file
 * This file is dynamically assembled from separate parts.
 * Some of these parts have 3rd party licenses or copyright information attached
 * Such information is valid for that section,
 * not for the entire composite file
 * originating files are separated by - filename.js -
 */

/* - ++resource++plone.app.event/event.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/++resource++plone.app.event/event.js?original=1
if(plone===undefined){var plone={}}(function($,plone){plone.paevent=plone.paevent||{};plone.paevent.end_start_delta=1/ 24;  //Delta in days
function a_or_b(a,b){var ret;if(a.length>0){ret=a} else{ret=b}
return ret}
function getDateTime(datetimewidget){var date,time,datetime;date=$('input[name="_submit"]:first',datetimewidget).prop('value');date=date.split("-");time=$('input[name="_submit"]:last',datetimewidget).prop('value')||'00:00';time=time.split(":");datetime=new Date(parseInt(date[0],10),parseInt(date[1],10)-1,parseInt(date[2],10),parseInt(time[0],10),parseInt(time[1],10));return datetime}
function initDelta(){var start_datetime,end_datetime;start_datetime=getDateTime(a_or_b($('#formfield-form-widgets-IEventBasic-start'),$('#archetypes-fieldname-startDate')));end_datetime=getDateTime(a_or_b($('#formfield-form-widgets-IEventBasic-end'),$('#archetypes-fieldname-endDate')));plone.paevent.end_start_delta=(end_datetime-start_datetime)/ 1000 / 60}
function updateEndDate(){var jq_start,jq_end,start_date,new_end_date;jq_start=a_or_b($('#formfield-form-widgets-IEventBasic-start'),$('#archetypes-fieldname-startDate'));jq_end=a_or_b($('#formfield-form-widgets-IEventBasic-end'),$('#archetypes-fieldname-endDate'));start_date=getDateTime(jq_start);new_end_date=new Date(start_date);new_end_date.setMinutes(start_date.getMinutes()+plone.paevent.end_start_delta);$('.pattern-pickadate-date',jq_end).pickadate('picker').set('select',new_end_date);$('.pattern-pickadate-time',jq_end).pickatime('picker').set('select',new_end_date)}
function validateEndDate(){var jq_start,jq_end,start_datetime,end_datetime;jq_start=a_or_b($('#formfield-form-widgets-IEventBasic-start'),$('#archetypes-fieldname-startDate'));jq_end=a_or_b($('#formfield-form-widgets-IEventBasic-end'),$('#archetypes-fieldname-endDate'));start_datetime=getDateTime(jq_start);end_datetime=getDateTime(jq_end);if(end_datetime<start_datetime){jq_end.addClass("error")} else{jq_end.removeClass("error")}}
function show_hide_widget(widget,hide,fade){var $widget=$(widget);if(hide===true){if(fade===true){$widget.fadeOut()}
else{$widget.hide()}} else{if(fade===true){$widget.fadeIn()}
else{$widget.show()}}}
function event_listing_calendar_init(cal){if($().dateinput&&cal.length>0){var get_req_param,val;get_req_param=function(name){if(name===(new RegExp('[?&]'+encodeURIComponent(name)+'=([^&]*)')).exec(window.location.search)){return decodeURIComponent(name[1])}};val=get_req_param('date');if(val===undefined){val=new Date()} else{val=new Date(val)}
cal.dateinput({selectors:true,trigger:true,format:'yyyy-mm-dd',yearRange:[-10,10],firstDay:1,value:val,change: function(){var value=this.getValue("yyyy-mm-dd");window.location.href='event_listing?mode=day&date='+value}}).unbind('change').bind('onShow', function(){var trigger_offset=$(this).next().offset();$(this).data('dateinput').getCalendar().offset({top:trigger_offset.top+20,left:trigger_offset.left})})}}
$(window).load(function(){var jq_whole_day,jq_time,jq_open_end,jq_end,jq_start;jq_whole_day=a_or_b($('#formfield-form-widgets-IEventBasic-whole_day input'),$('form[name="edit_form"] input#wholeDay'));jq_time=a_or_b($('#formfield-form-widgets-IEventBasic-start .pattern-pickadate-time-wrapper, #formfield-form-widgets-IEventBasic-end .pattern-pickadate-time-wrapper'),$('#archetypes-fieldname-startDate .pattern-pickadate-time-wrapper, #archetypes-fieldname-endDate .pattern-pickadate-time-wrapper'));if(jq_whole_day.length>0){jq_whole_day.bind('change', function(e){show_hide_widget(jq_time,e.target.checked,true)});show_hide_widget(jq_time,jq_whole_day.get(0).checked,false)}
jq_open_end=a_or_b($('#formfield-form-widgets-IEventBasic-open_end input'),$('form[name="edit_form"] input#openEnd'));jq_end=a_or_b($('#formfield-form-widgets-IEventBasic-end'),$('#archetypes-fieldname-endDate'));if(jq_open_end.length>0){jq_open_end.bind('change', function(e){show_hide_widget(jq_end,e.target.checked,true)});show_hide_widget(jq_end,jq_open_end.get(0).checked,false)}
jq_start=a_or_b($('#formfield-form-widgets-IEventBasic-start'),$('#archetypes-fieldname-startDate'));jq_start.each(function(){$(this).on('focus','.picker__input',initDelta);$(this).on('change','.picker__input',updateEndDate)});jq_end.each(function(){$(this).on('focus','.picker__input',initDelta);$(this).on('change','.picker__input',validateEndDate)});event_listing_calendar_init($("#event_listing_calendar"))})}(jQuery,plone));

/* - ++resource++plone.app.event.portlet_calendar.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/++resource++plone.app.event.portlet_calendar.js?original=1
(function($){
function load_portlet_calendar(event,elem){event.preventDefault();var pw,elem_data,portlethash,url;pw=elem.closest('.portletWrapper');elem_data=elem.data();portlethash=pw.attr('id');portlethash=portlethash.substring(15,portlethash.length);url=portal_url+'/@@render-portlet?portlethash='+portlethash+'&year='+elem_data.year+'&month='+elem_data.month;$.ajax({url:url,success: function(data){pw.html(data);rebind_portlet_calendar()}})}
function rebind_portlet_calendar(){$('.portletCalendar a.calendarNext').click(function(event){load_portlet_calendar(event,$(this))});$('.portletCalendar a.calendarPrevious').click(function(event){load_portlet_calendar(event,$(this))});$('.portletCalendar dd a[title]').tooltip({offset:[-10,0],tipClass:'pae_calendar_tooltip'})}
$(document).ready(function(){rebind_portlet_calendar()})}(jQuery));

/* - ++resource++collective.galleria.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/++resource++collective.galleria.js?original=1
(function($){var undef,window=this,doc=window.document,$doc=$(doc),$win=$(window),protoArray=Array.prototype,VERSION=1.29,DEBUG=true,TIMEOUT=30000,DUMMY=false,NAV=navigator.userAgent.toLowerCase(),HASH=window.location.hash.replace(/#\//,''),F=function(){},FALSE=function(){return false},IE=(function(){var v=3,div=doc.createElement('div'),all=div.getElementsByTagName('i');do{div.innerHTML='<!--[if gt IE '+(++v)+']><i></i><![endif]-->'} while(all[0]);return v>4?v:undef}()),DOM=function(){return{html:doc.documentElement,body:doc.body,head:doc.getElementsByTagName('head')[0],title:doc.title}},IFRAME=window.parent!==window.self,_eventlist='data ready thumbnail loadstart loadfinish image play pause progress '+'fullscreen_enter fullscreen_exit idle_enter idle_exit rescale '+'lightbox_open lightbox_close lightbox_image',_events=(function(){var evs=[];$.each(_eventlist.split(' '), function(i,ev){evs.push(ev);if(/_/.test(ev)){evs.push(ev.replace(/_/g,''))}});return evs}()),_legacyOptions=function(options){var n;if(typeof options!=='object'){return options}
$.each(options, function(key,value){if(/^[a-z]+_/.test(key)){n='';$.each(key.split('_'), function(i,k){n+=i>0?k.substr(0,1).toUpperCase()+k.substr(1):k});options[n]=value;delete options[key]}});return options},_patchEvent=function(type){if($.inArray(type,_events)>-1){return Galleria[type.toUpperCase()]}
return type},_video={youtube:{reg:/https?:\/\/(?:[a-zA_Z]{2,3}.)?(?:youtube\.com\/watch\?)((?:[\w\d\-\_\=]+&amp;(?:amp;)?)*v(?:&lt;[A-Z]+&gt;)?=([0-9a-zA-Z\-\_]+))/i,embed: function(id){return 'http://www.youtube.com/embed/'+id},getThumb: function(id,success,fail){fail=fail||F;$.getJSON(window.location.protocol+'//gdata.youtube.com/feeds/api/videos/'+id+'?v=2&alt=json-in-script&callback=?', function(data){try{success(data.entry.media$group.media$thumbnail[0].url)} catch(e){fail()}}).error(fail)}},vimeo:{reg:/https?:\/\/(?:www\.)?(vimeo\.com)\/(?:hd#)?([0-9]+)/i,embed: function(id){return 'http://player.vimeo.com/video/'+id},getThumb: function(id,success,fail){fail=fail||F;$.getJSON('http://vimeo.com/api/v2/video/'+id+'.json?callback=?', function(data){try{success(data[0].thumbnail_medium)} catch(e){fail()}}).error(fail)}},dailymotion:{reg:/https?:\/\/(?:www\.)?(dailymotion\.com)\/video\/([^_]+)/,embed: function(id){return 'http://www.dailymotion.com/embed/video/'+id},getThumb: function(id,success,fail){fail=fail||F;$.getJSON('https://api.dailymotion.com/video/'+id+'?fields=thumbnail_medium_url&callback=?', function(data){try{success(data.thumbnail_medium_url)} catch(e){fail()}}).error(fail)}}},_videoTest=function(url){var match;for(var v in _video){match=url&&url.match(_video[v].reg);if(match&&match.length){return{id:match[2],provider:v}}}
return false},_nativeFullscreen={support:(function(){var html=DOM().html;return!IFRAME&&(html.requestFullscreen||html.mozRequestFullScreen||html.webkitRequestFullScreen)}()),callback:F,enter: function(instance,callback,elem){this.instance=instance;this.callback=callback||F;elem=elem||DOM().html;if(elem.requestFullscreen){elem.requestFullscreen()}
else if(elem.mozRequestFullScreen){elem.mozRequestFullScreen()}
else if(elem.webkitRequestFullScreen){elem.webkitRequestFullScreen()}},exit: function(callback){this.callback=callback||F;if(doc.exitFullscreen){doc.exitFullscreen()}
else if(doc.mozCancelFullScreen){doc.mozCancelFullScreen()}
else if(doc.webkitCancelFullScreen){doc.webkitCancelFullScreen()}},instance:null,listen: function(){if(!this.support){return}
var handler=function(){if(!_nativeFullscreen.instance){return}
var fs=_nativeFullscreen.instance._fullscreen;if(doc.fullscreen||doc.mozFullScreen||doc.webkitIsFullScreen){fs._enter(_nativeFullscreen.callback)} else{fs._exit(_nativeFullscreen.callback)}};doc.addEventListener('fullscreenchange',handler,false);doc.addEventListener('mozfullscreenchange',handler,false);doc.addEventListener('webkitfullscreenchange',handler,false)}},_galleries=[],_instances=[],_hasError=false,_canvas=false,_pool=[],_themeLoad=function(theme){Galleria.theme=theme;$.each(_pool, function(i,instance){if(!instance._initialized){instance._init.call(instance)}});_pool=[]},Utils=(function(){return{clearTimer: function(id){$.each(Galleria.get(), function(){this.clearTimer(id)})},addTimer: function(id){$.each(Galleria.get(), function(){this.addTimer(id)})},array: function(obj){return protoArray.slice.call(obj,0)},create: function(className,nodeName){nodeName=nodeName||'div';var elem=doc.createElement(nodeName);elem.className=className;return elem},removeFromArray: function(arr,elem){$.each(arr, function(i,el){if(el==elem){arr.splice(i,1);return false}});return arr},getScriptPath: function(src){src=src||$('script:last').attr('src');var slices=src.split('/');if(slices.length==1){return ''}
slices.pop();return slices.join('/')+'/'},animate:(function(){var transition=(function(style){var props='transition WebkitTransition MozTransition OTransition'.split(' '),i;if(window.opera){return false}
for(i=0;props[i];i++){if(typeof style[props[i]]!=='undefined'){return props[i]}}
return false}((doc.body||doc.documentElement).style));var endEvent={MozTransition:'transitionend',OTransition:'oTransitionEnd',WebkitTransition:'webkitTransitionEnd',transition:'transitionend'}[transition];var easings={_default:[0.25,0.1,0.25,1],galleria:[0.645,0.045,0.355,1],galleriaIn:[0.55,0.085,0.68,0.53],galleriaOut:[0.25,0.46,0.45,0.94],ease:[0.25,0,0.25,1],linear:[0.25,0.25,0.75,0.75],'ease-in':[0.42,0,1,1],'ease-out':[0,0,0.58,1],'ease-in-out':[0.42,0,0.58,1]};var setStyle=function(elem,value,suffix){var css={};suffix=suffix||'transition';$.each('webkit moz ms o'.split(' '), function(){css['-'+this+'-'+suffix]=value});elem.css(css)};var clearStyle=function(elem){setStyle(elem,'none','transition');if(Galleria.WEBKIT&&Galleria.TOUCH){setStyle(elem,'translate3d(0,0,0)','transform');if(elem.data('revert')){elem.css(elem.data('revert'));elem.data('revert',null)}}};var change,strings,easing,syntax,revert,form,css;return function(elem,to,options){options=$.extend({duration:400,complete:F,stop:false},options);elem=$(elem);if(!options.duration){elem.css(to);options.complete.call(elem[0]);return}
if(!transition){elem.animate(to,options);return}
if(options.stop){elem.unbind(endEvent);clearStyle(elem)}
change=false;$.each(to, function(key,val){css=elem.css(key);if(Utils.parseValue(css)!=Utils.parseValue(val)){change=true}
elem.css(key,css)});if(!change){window.setTimeout( function(){options.complete.call(elem[0])},options.duration);return}
strings=[];easing=options.easing in easings?easings[options.easing]:easings._default;syntax=' '+options.duration+'ms'+' cubic-bezier('+easing.join(',')+')';window.setTimeout((function(elem,endEvent,to,syntax){return function(){elem.one(endEvent,(function(elem){return function(){clearStyle(elem);options.complete.call(elem[0])}}(elem)));if(Galleria.WEBKIT&&Galleria.TOUCH){revert={};form=[0,0,0];$.each(['left','top'], function(i,m){if(m in to){form[i]=(Utils.parseValue(to[m])-Utils.parseValue(elem.css(m)))+'px';revert[m]=to[m];delete to[m]}});if(form[0]||form[1]){elem.data('revert',revert);strings.push('-webkit-transform'+syntax);setStyle(elem,'translate3d('+form.join(',')+')','transform')}}
$.each(to, function(p,val){strings.push(p+syntax)});setStyle(elem,strings.join(','));elem.css(to)}}(elem,endEvent,to,syntax)),2)}}()),removeAlpha: function(elem){if(IE<9&&elem){var style=elem.style,currentStyle=elem.currentStyle,filter=currentStyle&&currentStyle.filter||style.filter||"";if(/alpha/.test(filter)){style.filter=filter.replace(/alpha\([^)]*\)/i,'')}}},forceStyles: function(elem,styles){elem=$(elem);if(elem.attr('style')){elem.data('styles',elem.attr('style')).removeAttr('style')}
elem.css(styles)},revertStyles: function(){$.each(Utils.array(arguments), function(i,elem){elem=$(elem);elem.removeAttr('style');elem.attr('style','');if(elem.data('styles')){elem.attr('style',elem.data('styles')).data('styles',null)}})},moveOut: function(elem){Utils.forceStyles(elem,{position:'absolute',left:-10000})},moveIn: function(){Utils.revertStyles.apply(Utils,Utils.array(arguments))},elem: function(elem){if(elem instanceof $){return{$:elem,dom:elem[0]}} else{return{$:$(elem),dom:elem}}},hide: function(elem,speed,callback){callback=callback||F;var el=Utils.elem(elem),$elem=el.$;elem=el.dom;if(!$elem.data('opacity')){$elem.data('opacity',$elem.css('opacity'))}
var style={opacity:0};if(speed){var complete=IE<9&&elem? function(){Utils.removeAlpha(elem);elem.style.visibility='hidden';callback.call(elem)}:callback;Utils.animate(elem,style,{duration:speed,complete:complete,stop:true})} else{if(IE<9&&elem){Utils.removeAlpha(elem);elem.style.visibility='hidden'} else{$elem.css(style)}}},show: function(elem,speed,callback){callback=callback||F;var el=Utils.elem(elem),$elem=el.$;elem=el.dom;var saved=parseFloat($elem.data('opacity'))||1,style={opacity:saved};if(speed){if(IE<9){$elem.css('opacity',0);elem.style.visibility='visible'}
var complete=IE<9&&elem? function(){if(style.opacity==1){Utils.removeAlpha(elem)}
callback.call(elem)}:callback;Utils.animate(elem,style,{duration:speed,complete:complete,stop:true})} else{if(IE<9&&style.opacity==1&&elem){Utils.removeAlpha(elem);elem.style.visibility='visible'} else{$elem.css(style)}}},optimizeTouch:(function(){var node,evs,fakes,travel,evt={},handler=function(e){e.preventDefault();evt=$.extend({},e,true)},attach=function(){this.evt=evt},fake=function(){this.handler.call(node,this.evt)};return function(elem){$(elem).bind('touchend', function(e){node=e.target;travel=true;while(node.parentNode&&node!=e.currentTarget&&travel){evs=$(node).data('events');fakes=$(node).data('fakes');if(evs&&'click' in evs){travel=false;e.preventDefault();$(node).click(handler).click();evs.click.pop();$.each(evs.click,attach);$(node).data('fakes',evs.click);delete evs.click} else if(fakes){travel=false;e.preventDefault();$.each(fakes,fake)}
node=node.parentNode}})}}()),wait: function(options){options=$.extend({until:FALSE,success:F,error: function(){Galleria.raise('Could not complete wait function.')},timeout:3000},options);var start=Utils.timestamp(),elapsed,now,fn=function(){now=Utils.timestamp();elapsed=now-start;if(options.until(elapsed)){options.success();return false}
if(typeof options.timeout=='number'&&now>=start+options.timeout){options.error();return false}
window.setTimeout(fn,10)};window.setTimeout(fn,10)},toggleQuality: function(img,force){if((IE!==7&&IE!==8)||!img||img.nodeName.toUpperCase()!='IMG'){return}
if(typeof force==='undefined'){force=img.style.msInterpolationMode==='nearest-neighbor'}
img.style.msInterpolationMode=force?'bicubic':'nearest-neighbor'},insertStyleTag: function(styles,id){if(id&&$('#'+id).length){return}
var style=doc.createElement('style');if(id){style.id=id}
DOM().head.appendChild(style);if(style.styleSheet){style.styleSheet.cssText=styles} else{var cssText=doc.createTextNode(styles);style.appendChild(cssText)}},loadScript: function(url,callback){var done=false,script=$('<scr'+'ipt>').attr({src:url,async:true}).get(0);script.onload=script.onreadystatechange=function(){if(!done&&(!this.readyState||this.readyState==='loaded'||this.readyState==='complete')){done=true;script.onload=script.onreadystatechange=null;if(typeof callback==='function'){callback.call(this,this)}}};DOM().head.appendChild(script)},parseValue: function(val){if(typeof val==='number'){return val} else if(typeof val==='string'){var arr=val.match(/\-?\d|\./g);return arr&&arr.constructor===Array?arr.join('')*1:0} else{return 0}},timestamp: function(){return new Date().getTime()},loadCSS: function(href,id,callback){var link,length;$('link[rel=stylesheet]').each(function(){if(new RegExp(href).test(this.href)){link=this;return false}});if(typeof id==='function'){callback=id;id=undef}
callback=callback||F;if(link){callback.call(link,link);return link}
length=doc.styleSheets.length;if($('#'+id).length){$('#'+id).attr('href',href);length--} else{link=$('<link>').attr({rel:'stylesheet',href:href,id:id}).get(0);var styles=$('link[rel="stylesheet"], style');if(styles.length){styles.get(0).parentNode.insertBefore(link,styles[0])} else{DOM().head.appendChild(link)}
if(IE){if(length>=31){Galleria.raise('You have reached the browser stylesheet limit (31)',true);return}}}
if(typeof callback==='function'){var $loader=$('<s>').attr('id','galleria-loader').hide().appendTo(DOM().body);Utils.wait({until: function(){return $loader.height()==1},success: function(){$loader.remove();callback.call(link,link)},error: function(){$loader.remove();Galleria.raise('Theme CSS could not load after 20 sec. '+Galleria.QUIRK?'Your browser is in Quirks Mode, please add a correct doctype.':'Please download the latest theme at http://galleria.io/customer/.',true)},timeout:20000})}
return link}}}()),_transitions=(function(){var _slide=function(params,complete,fade,door){var easing=this.getOptions('easing'),distance=this.getStageWidth(),from={left:distance *(params.rewind?-1:1)},to={left:0};if(fade){from.opacity=0;to.opacity=1} else{from.opacity=1}
$(params.next).css(from);Utils.animate(params.next,to,{duration:params.speed,complete:(function(elems){return function(){complete();elems.css({left:0})}}($(params.next).add(params.prev))),queue:false,easing:easing});if(door){params.rewind=!params.rewind}
if(params.prev){from={left:0};to={left:distance *(params.rewind?1:-1)};if(fade){from.opacity=1;to.opacity=0}
$(params.prev).css(from);Utils.animate(params.prev,to,{duration:params.speed,queue:false,easing:easing,complete: function(){$(this).css('opacity',0)}})}};return{active:false,init: function(effect,params,complete){if(_transitions.effects.hasOwnProperty(effect)){_transitions.effects[effect].call(this,params,complete)}},effects:{fade: function(params,complete){$(params.next).css({opacity:0,left:0});Utils.animate(params.next,{opacity:1},{duration:params.speed,complete:complete});if(params.prev){$(params.prev).css('opacity',1).show();Utils.animate(params.prev,{opacity:0},{duration:params.speed})}},flash: function(params,complete){$(params.next).css({opacity:0,left:0});if(params.prev){Utils.animate(params.prev,{opacity:0},{duration:params.speed/2,complete: function(){Utils.animate(params.next,{opacity:1},{duration:params.speed,complete:complete})}})} else{Utils.animate(params.next,{opacity:1},{duration:params.speed,complete:complete})}},pulse: function(params,complete){if(params.prev){$(params.prev).hide()}
$(params.next).css({opacity:0,left:0}).show();Utils.animate(params.next,{opacity:1},{duration:params.speed,complete:complete})},slide: function(params,complete){_slide.apply(this,Utils.array(arguments))},fadeslide: function(params,complete){_slide.apply(this,Utils.array(arguments).concat([true]))},doorslide: function(params,complete){_slide.apply(this,Utils.array(arguments).concat([false,true]))}}}}());_nativeFullscreen.listen();Galleria=function(){var self=this;this._options={};this._playing=false;this._playtime=5000;this._active=null;this._queue={length:0};this._data=[];this._dom={};this._thumbnails=[];this._layers=[];this._initialized=false;this._firstrun=false;this._stageWidth=0;this._stageHeight=0;this._target=undef;this._binds=[];this._id=parseInt(Math.random()*10000,10);var divs='container stage images image-nav image-nav-left image-nav-right '+'info info-text info-title info-description '+'thumbnails thumbnails-list thumbnails-container thumb-nav-left thumb-nav-right '+'loader counter tooltip',spans='current total';$.each(divs.split(' '), function(i,elemId){self._dom[elemId]=Utils.create('galleria-'+elemId)});$.each(spans.split(' '), function(i,elemId){self._dom[elemId]=Utils.create('galleria-'+elemId,'span')});var keyboard=this._keyboard={keys:{'UP':38,'DOWN':40,'LEFT':37,'RIGHT':39,'RETURN':13,'ESCAPE':27,'BACKSPACE':8,'SPACE':32},map:{},bound:false,press: function(e){var key=e.keyCode||e.which;if(key in keyboard.map&&typeof keyboard.map[key]==='function'){keyboard.map[key].call(self,e)}},attach: function(map){var key,up;for(key in map){if(map.hasOwnProperty(key)){up=key.toUpperCase();if(up in keyboard.keys){keyboard.map[keyboard.keys[up]]=map[key]} else{keyboard.map[up]=map[key]}}}
if(!keyboard.bound){keyboard.bound=true;$doc.bind('keydown',keyboard.press)}},detach: function(){keyboard.bound=false;keyboard.map={};$doc.unbind('keydown',keyboard.press)}};var controls=this._controls={0:undef,1:undef,active:0,swap: function(){controls.active=controls.active?0:1},getActive: function(){return controls[controls.active]},getNext: function(){return controls[1-controls.active]}};var carousel=this._carousel={next:self.$('thumb-nav-right'),prev:self.$('thumb-nav-left'),width:0,current:0,max:0,hooks:[],update: function(){var w=0,h=0,hooks=[0];$.each(self._thumbnails, function(i,thumb){if(thumb.ready){w+=thumb.outerWidth||$(thumb.container).outerWidth(true);hooks[i+1]=w;h=Math.max(h,thumb.outerHeight||$(thumb.container).outerHeight(true))}});self.$('thumbnails').css({width:w,height:h});carousel.max=w;carousel.hooks=hooks;carousel.width=self.$('thumbnails-list').width();carousel.setClasses();self.$('thumbnails-container').toggleClass('galleria-carousel',w>carousel.width);carousel.width=self.$('thumbnails-list').width()},bindControls: function(){var i;carousel.next.bind('click', function(e){e.preventDefault();if(self._options.carouselSteps==='auto'){for(i=carousel.current;i<carousel.hooks.length;i++){if(carousel.hooks[i]-carousel.hooks[carousel.current]>carousel.width){carousel.set(i-2);break}}} else{carousel.set(carousel.current+self._options.carouselSteps)}});carousel.prev.bind('click', function(e){e.preventDefault();if(self._options.carouselSteps==='auto'){for(i=carousel.current;i>=0;i--){if(carousel.hooks[carousel.current]-carousel.hooks[i]>carousel.width){carousel.set(i+2);break} else if(i===0){carousel.set(0);break}}} else{carousel.set(carousel.current-self._options.carouselSteps)}})},set: function(i){i=Math.max(i,0);while(carousel.hooks[i-1]+carousel.width>=carousel.max&&i>=0){i--}
carousel.current=i;carousel.animate()},getLast: function(i){return(i||carousel.current)-1},follow: function(i){if(i===0||i===carousel.hooks.length-2){carousel.set(i);return}
var last=carousel.current;while(carousel.hooks[last]-carousel.hooks[carousel.current]<carousel.width&&last<=carousel.hooks.length){last++}
if(i-1<carousel.current){carousel.set(i-1)} else if(i+2>last){carousel.set(i-last+carousel.current+2)}},setClasses: function(){carousel.prev.toggleClass('disabled',!carousel.current);carousel.next.toggleClass('disabled',carousel.hooks[carousel.current]+carousel.width>=carousel.max)},animate: function(to){carousel.setClasses();var num=carousel.hooks[carousel.current] *-1;if(isNaN(num)){return}
Utils.animate(self.get('thumbnails'),{left:num},{duration:self._options.carouselSpeed,easing:self._options.easing,queue:false})}};var tooltip=this._tooltip={initialized:false,open:false,timer:'tooltip'+self._id,swapTimer:'swap'+self._id,init: function(){tooltip.initialized=true;var css='.galleria-tooltip{padding:3px 8px;max-width:50%;background:#ffe;color:#000;z-index:3;position:absolute;font-size:11px;line-height:1.3;'+'opacity:0;box-shadow:0 0 2px rgba(0,0,0,.4);-moz-box-shadow:0 0 2px rgba(0,0,0,.4);-webkit-box-shadow:0 0 2px rgba(0,0,0,.4);}';Utils.insertStyleTag(css,'galleria-tooltip');self.$('tooltip').css({opacity:0.8,visibility:'visible',display:'none'})},move: function(e){var mouseX=self.getMousePosition(e).x,mouseY=self.getMousePosition(e).y,$elem=self.$('tooltip'),x=mouseX,y=mouseY,height=$elem.outerHeight(true)+1,width=$elem.outerWidth(true),limitY=height+15;var maxX=self.$('container').width()-width-2,maxY=self.$('container').height()-height-2;if(!isNaN(x)&&!isNaN(y)){x+=10;y-=(height+8);x=Math.max(0,Math.min(maxX,x));y=Math.max(0,Math.min(maxY,y));if(mouseY<limitY){y=limitY}
$elem.css({left:x,top:y})}},bind: function(elem,value){if(Galleria.TOUCH){return}
if(!tooltip.initialized){tooltip.init()}
var mouseout=function(){self.$('container').unbind('mousemove',tooltip.move);self.clearTimer(tooltip.timer);self.$('tooltip').stop().animate({opacity:0},200, function(){self.$('tooltip').hide();self.addTimer(tooltip.swapTimer, function(){tooltip.open=false},1000)})};var hover=function(elem,value){tooltip.define(elem,value);$(elem).hover(function(){self.clearTimer(tooltip.swapTimer);self.$('container').unbind('mousemove',tooltip.move).bind('mousemove',tooltip.move).trigger('mousemove');tooltip.show(elem);self.addTimer(tooltip.timer, function(){self.$('tooltip').stop().show().animate({opacity:1});tooltip.open=true},tooltip.open?0:500)},mouseout).click(mouseout)};if(typeof value==='string'){hover((elem in self._dom?self.get(elem):elem),value)} else{$.each(elem, function(elemID,val){hover(self.get(elemID),val)})}},show: function(elem){elem=$(elem in self._dom?self.get(elem):elem);var text=elem.data('tt'),mouseup=function(e){window.setTimeout((function(ev){return function(){tooltip.move(ev)}}(e)),10);elem.unbind('mouseup',mouseup)};text=typeof text==='function'?text():text;if(!text){return}
self.$('tooltip').html(text.replace(/\s/,'&#160;'));elem.bind('mouseup',mouseup)},define: function(elem,value){if(typeof value!=='function'){var s=value;value=function(){return s}}
elem=$(elem in self._dom?self.get(elem):elem).data('tt',value);tooltip.show(elem)}};var fullscreen=this._fullscreen={scrolled:0,crop:undef,active:false,keymap:self._keyboard.map,parseCallback: function(callback,enter){return _transitions.active? function(){if(typeof callback=='function'){callback.call(self)}
var active=self._controls.getActive(),next=self._controls.getNext();self._scaleImage(next);self._scaleImage(active);if(enter&&self._options.trueFullscreen){$(active.container).add(next.container).trigger('transitionend')}}:callback},enter: function(callback){callback=fullscreen.parseCallback(callback,true);if(self._options.trueFullscreen&&_nativeFullscreen.support){fullscreen.active=true;Utils.forceStyles(self.get('container'),{width:'100%',height:'100%'});self.rescale();if(Galleria.MAC){if(Galleria.WEBKIT){self.$('container').css('opacity',0).addClass('fullscreen');window.setTimeout(function(){fullscreen.scale();self.$('container').css('opacity',1)},50)} else{self.$('stage').css('opacity',0);window.setTimeout(function(){fullscreen.scale();self.$('stage').css('opacity',1)},4)}} else{self.$('container').addClass('fullscreen')}
$win.resize(fullscreen.scale);_nativeFullscreen.enter(self,callback,self.get('container'))} else{fullscreen.scrolled=$win.scrollTop();window.scrollTo(0,0);fullscreen._enter(callback)}},_enter: function(callback){fullscreen.active=true;if(IFRAME){fullscreen.iframe=(function(){var elem,refer=doc.referrer,test=doc.createElement('a'),loc=window.location;test.href=refer;if(test.protocol!=loc.protocol||test.hostname!=loc.hostname||test.port!=loc.port){Galleria.raise('Parent fullscreen not available. Iframe protocol, domains and ports must match.');return false}
fullscreen.pd=window.parent.document;$(fullscreen.pd).find('iframe').each(function(){var idoc=this.contentDocument||this.contentWindow.document;if(idoc===doc){elem=this;return false}});return elem}())}
Utils.hide(self.getActiveImage());if(IFRAME&&fullscreen.iframe){fullscreen.iframe.scrolled=$(window.parent).scrollTop();window.parent.scrollTo(0,0)}
var data=self.getData(),options=self._options,inBrowser=!self._options.trueFullscreen||!_nativeFullscreen.support,htmlbody={height:'100%',overflow:'hidden',margin:0,padding:0};if(inBrowser){self.$('container').addClass('fullscreen');Utils.forceStyles(self.get('container'),{position:'fixed',top:0,left:0,width:'100%',height:'100%',zIndex:10000});Utils.forceStyles(DOM().html,htmlbody);Utils.forceStyles(DOM().body,htmlbody)}
if(IFRAME&&fullscreen.iframe){Utils.forceStyles(fullscreen.pd.documentElement,htmlbody);Utils.forceStyles(fullscreen.pd.body,htmlbody);Utils.forceStyles(fullscreen.iframe,$.extend(htmlbody,{width:'100%',height:'100%',top:0,left:0,position:'fixed',zIndex:10000,border:'none'}))}
fullscreen.keymap=$.extend({},self._keyboard.map);self.attachKeyboard({escape:self.exitFullscreen,right:self.next,left:self.prev});fullscreen.crop=options.imageCrop;if(options.fullscreenCrop!=undef){options.imageCrop=options.fullscreenCrop}
if(data&&data.big&&data.image!==data.big){var big=new Galleria.Picture(),cached=big.isCached(data.big),index=self.getIndex(),thumb=self._thumbnails[index];self.trigger({type:Galleria.LOADSTART,cached:cached,rewind:false,index:index,imageTarget:self.getActiveImage(),thumbTarget:thumb,galleriaData:data});big.load(data.big, function(big){self._scaleImage(big,{complete: function(big){self.trigger({type:Galleria.LOADFINISH,cached:cached,index:index,rewind:false,imageTarget:big.image,thumbTarget:thumb});var image=self._controls.getActive().image;if(image){$(image).width(big.image.width).height(big.image.height).attr('style',$(big.image).attr('style')).attr('src',big.image.src)}}})})}
self.rescale(function(){self.addTimer(false, function(){if(inBrowser){Utils.show(self.getActiveImage())}
if(typeof callback==='function'){callback.call(self)}},100);self.trigger(Galleria.FULLSCREEN_ENTER)});if(!inBrowser){Utils.show(self.getActiveImage())} else{$win.resize(fullscreen.scale)}},scale: function(){self.rescale()},exit: function(callback){callback=fullscreen.parseCallback(callback);if(self._options.trueFullscreen&&_nativeFullscreen.support){_nativeFullscreen.exit(callback)} else{fullscreen._exit(callback)}},_exit: function(callback){fullscreen.active=false;var inBrowser=!self._options.trueFullscreen||!_nativeFullscreen.support;self.$('container').removeClass('fullscreen');if(inBrowser){Utils.hide(self.getActiveImage());Utils.revertStyles(self.get('container'),DOM().html,DOM().body);window.scrollTo(0,fullscreen.scrolled)}
if(IFRAME&&fullscreen.iframe){Utils.revertStyles(fullscreen.pd.documentElement,fullscreen.pd.body,fullscreen.iframe);if(fullscreen.iframe.scrolled){window.parent.scrollTo(0,fullscreen.iframe.scrolled)}}
self.detachKeyboard();self.attachKeyboard(fullscreen.keymap);self._options.imageCrop=fullscreen.crop;var big=self.getData().big,image=self._controls.getActive().image;if(!self.getData().iframe&&image&&big&&big==image.src){window.setTimeout(function(src){return function(){image.src=src}}(self.getData().image),1)}
self.rescale(function(){self.addTimer(false, function(){if(inBrowser){Utils.show(self.getActiveImage())}
if(typeof callback==='function'){callback.call(self)}
$win.trigger('resize')},50);self.trigger(Galleria.FULLSCREEN_EXIT)});$win.unbind('resize',fullscreen.scale)}};var idle=this._idle={trunk:[],bound:false,active:false,add: function(elem,to,from,hide){if(!elem){return}
if(!idle.bound){idle.addEvent()}
elem=$(elem);if(typeof from=='boolean'){hide=from;from={}}
from=from||{};var extract={},style;for(style in to){if(to.hasOwnProperty(style)){extract[style]=elem.css(style)}}
elem.data('idle',{from:$.extend(extract,from),to:to,complete:true,busy:false});if(!hide){idle.addTimer()} else{elem.css(to)}
idle.trunk.push(elem)},remove: function(elem){elem=$(elem);$.each(idle.trunk, function(i,el){if(el&&el.length&&!el.not(elem).length){elem.css(elem.data('idle').from);idle.trunk.splice(i,1)}});if(!idle.trunk.length){idle.removeEvent();self.clearTimer(idle.timer)}},addEvent: function(){idle.bound=true;self.$('container').bind('mousemove click',idle.showAll);if(self._options.idleMode=='hover'){self.$('container').bind('mouseleave',idle.hide)}},removeEvent: function(){idle.bound=false;self.$('container').bind('mousemove click',idle.showAll);if(self._options.idleMode=='hover'){self.$('container').unbind('mouseleave',idle.hide)}},addTimer: function(){if(self._options.idleMode=='hover'){return}
self.addTimer('idle', function(){idle.hide()},self._options.idleTime)},hide: function(){if(!self._options.idleMode||self.getIndex()===false||self.getData().iframe){return}
self.trigger(Galleria.IDLE_ENTER);var len=idle.trunk.length;$.each(idle.trunk, function(i,elem){var data=elem.data('idle');if(!data){return}
elem.data('idle').complete=false;Utils.animate(elem,data.to,{duration:self._options.idleSpeed,complete: function(){if(i==len-1){idle.active=false}}})})},showAll: function(){self.clearTimer('idle');$.each(idle.trunk, function(i,elem){idle.show(elem)})},show: function(elem){var data=elem.data('idle');if(!idle.active||(!data.busy&&!data.complete)){data.busy=true;self.trigger(Galleria.IDLE_EXIT);self.clearTimer('idle');Utils.animate(elem,data.from,{duration:self._options.idleSpeed/2,complete: function(){idle.active=true;$(elem).data('idle').busy=false;$(elem).data('idle').complete=true}})}
idle.addTimer()}};var lightbox=this._lightbox={width:0,height:0,initialized:false,active:null,image:null,elems:{},keymap:false,init: function(){self.trigger(Galleria.LIGHTBOX_OPEN);if(lightbox.initialized){return}
lightbox.initialized=true;var elems='overlay box content shadow title info close prevholder prev nextholder next counter image',el={},op=self._options,css='',abs='position:absolute;',prefix='lightbox-',cssMap={overlay:'position:fixed;display:none;opacity:'+op.overlayOpacity+';filter:alpha(opacity='+(op.overlayOpacity*100)+');top:0;left:0;width:100%;height:100%;background:'+op.overlayBackground+';z-index:99990',box:'position:fixed;display:none;width:400px;height:400px;top:50%;left:50%;margin-top:-200px;margin-left:-200px;z-index:99991',shadow:abs+'background:#000;width:100%;height:100%;',content:abs+'background-color:#fff;top:10px;left:10px;right:10px;bottom:10px;overflow:hidden',info:abs+'bottom:10px;left:10px;right:10px;color:#444;font:11px/13px arial,sans-serif;height:13px',close:abs+'top:10px;right:10px;height:20px;width:20px;background:#fff;text-align:center;cursor:pointer;color:#444;font:16px/22px arial,sans-serif;z-index:99999',image:abs+'top:10px;left:10px;right:10px;bottom:30px;overflow:hidden;display:block;',prevholder:abs+'width:50%;top:0;bottom:40px;cursor:pointer;',nextholder:abs+'width:50%;top:0;bottom:40px;right:-1px;cursor:pointer;',prev:abs+'top:50%;margin-top:-20px;height:40px;width:30px;background:#fff;left:20px;display:none;text-align:center;color:#000;font:bold 16px/36px arial,sans-serif',next:abs+'top:50%;margin-top:-20px;height:40px;width:30px;background:#fff;right:20px;left:auto;display:none;font:bold 16px/36px arial,sans-serif;text-align:center;color:#000',title:'float:left',counter:'float:right;margin-left:8px;'},hover=function(elem){return elem.hover(
function(){$(this).css('color','#bbb')},
function(){$(this).css('color','#444')})},appends={};if(IE&&IE>7){cssMap.nextholder+='background:#000;filter:alpha(opacity=0);';cssMap.prevholder+='background:#000;filter:alpha(opacity=0);'}
$.each(cssMap, function(key,value){css+='.galleria-'+prefix+key+'{'+value+'}'});css+='.galleria-'+prefix+'box.iframe .galleria-'+prefix+'prevholder,'+'.galleria-'+prefix+'box.iframe .galleria-'+prefix+'nextholder{'+'width:100px;height:100px;top:50%;margin-top:-70px}';Utils.insertStyleTag(css,'galleria-lightbox');$.each(elems.split(' '), function(i,elemId){self.addElement('lightbox-'+elemId);el[elemId]=lightbox.elems[elemId]=self.get('lightbox-'+elemId)});lightbox.image=new Galleria.Picture();$.each({box:'shadow content close prevholder nextholder',info:'title counter',content:'info image',prevholder:'prev',nextholder:'next'}, function(key,val){var arr=[];$.each(val.split(' '), function(i,prop){arr.push(prefix+prop)});appends[prefix+key]=arr});self.append(appends);$(el.image).append(lightbox.image.container);$(DOM().body).append(el.overlay,el.box);Utils.optimizeTouch(el.box);hover($(el.close).bind('click',lightbox.hide).html('&#215;'));$.each(['Prev','Next'], function(i,dir){var $d=$(el[dir.toLowerCase()]).html(/v/.test(dir)?'&#8249;&#160;':'&#160;&#8250;'),$e=$(el[dir.toLowerCase()+'holder']);$e.bind('click', function(){lightbox['show'+dir]()});if(IE<8||Galleria.TOUCH){$d.show();return}
$e.hover( function(){$d.show()}, function(e){$d.stop().fadeOut(200)})});$(el.overlay).bind('click',lightbox.hide);if(Galleria.IPAD){self._options.lightboxTransitionSpeed=0}},rescale: function(event){var width=Math.min($win.width()-40,lightbox.width),height=Math.min($win.height()-60,lightbox.height),ratio=Math.min(width/ lightbox.width, height / lightbox.height),destWidth=Math.round(lightbox.width * ratio)+40,destHeight=Math.round(lightbox.height * ratio)+60,to={width:destWidth,height:destHeight,'margin-top':Math.ceil(destHeight/2) *-1,'margin-left':Math.ceil(destWidth/2) *-1};if(event){$(lightbox.elems.box).css(to)} else{$(lightbox.elems.box).animate(to,{duration:self._options.lightboxTransitionSpeed,easing:self._options.easing,complete: function(){var image=lightbox.image,speed=self._options.lightboxFadeSpeed;self.trigger({type:Galleria.LIGHTBOX_IMAGE,imageTarget:image.image});$(image.container).show();$(image.image).animate({opacity:1},speed);Utils.show(lightbox.elems.info,speed)}})}},hide: function(){lightbox.image.image=null;$win.unbind('resize',lightbox.rescale);$(lightbox.elems.box).hide();Utils.hide(lightbox.elems.info);self.detachKeyboard();self.attachKeyboard(lightbox.keymap);lightbox.keymap=false;Utils.hide(lightbox.elems.overlay,200, function(){$(this).hide().css('opacity',self._options.overlayOpacity);self.trigger(Galleria.LIGHTBOX_CLOSE)})},showNext: function(){lightbox.show(self.getNext(lightbox.active))},showPrev: function(){lightbox.show(self.getPrev(lightbox.active))},show: function(index){lightbox.active=index=typeof index==='number'?index:self.getIndex()||0;if(!lightbox.initialized){lightbox.init()}
if(!lightbox.keymap){lightbox.keymap=$.extend({},self._keyboard.map);self.attachKeyboard({escape:lightbox.hide,right:lightbox.showNext,left:lightbox.showPrev})}
$win.unbind('resize',lightbox.rescale);var data=self.getData(index),total=self.getDataLength(),n=self.getNext(index),ndata,p,i;Utils.hide(lightbox.elems.info);try{for(i=self._options.preload;i>0;i--){p=new Galleria.Picture();ndata=self.getData(n);p.preload('big' in ndata?ndata.big:ndata.image);n=self.getNext(n)}} catch(e){}
lightbox.image.isIframe=!!data.iframe;$(lightbox.elems.box).toggleClass('iframe',!!data.iframe);lightbox.image.load(data.iframe||data.big||data.image, function(image){if(image.isIframe){var cw=$(window).width(),ch=$(window).height();if(self._options.maxVideoSize){var r=Math.min(self._options.maxVideoSize/cw,self._options.maxVideoSize/ch);if(r<1){cw *=r;ch *=r}}
lightbox.width=cw;lightbox.height=ch} else{lightbox.width=image.original.width;lightbox.height=image.original.height}
$(image.image).css({width:image.isIframe?'100%':'100.1%',height:image.isIframe?'100%':'100.1%',top:0,zIndex:99998,opacity:0,visibility:'visible'});lightbox.elems.title.innerHTML=data.title||'';lightbox.elems.counter.innerHTML=(index+1)+' / '+total;$win.resize(lightbox.rescale);lightbox.rescale()});$(lightbox.elems.overlay).show().css('visibility','visible');$(lightbox.elems.box).show()}};var _timer=this._timer={trunk:{},add: function(id,fn,delay,loop){id=id||new Date().getTime();loop=loop||false;this.clear(id);if(loop){var old=fn;fn=function(){old();_timer.add(id,fn,delay)}}
this.trunk[id]=window.setTimeout(fn,delay)},clear: function(id){var del=function(i){window.clearTimeout(this.trunk[i]);delete this.trunk[i]},i;if(!!id&&id in this.trunk){del.call(this,id)} else if(typeof id==='undefined'){for(i in this.trunk){if(this.trunk.hasOwnProperty(i)){del.call(this,i)}}}}};return this};Galleria.prototype={constructor:Galleria,init: function(target,options){var self=this;options=_legacyOptions(options);this._original={target:target,options:options,data:null};this._target=this._dom.target=target.nodeName?target:$(target).get(0);this._original.html=this._target.innerHTML;_instances.push(this);if(!this._target){Galleria.raise('Target not found',true);return}
this._options={autoplay:false,carousel:true,carouselFollow:true,carouselSpeed:400,carouselSteps:'auto',clicknext:false,dailymotion:{foreground:'%23EEEEEE',highlight:'%235BCEC5',background:'%23222222',logo:0,hideInfos:1},dataConfig: function(elem){return{}},dataSelector:'img',dataSort:false,dataSource:this._target,debug:undef,dummy:undef,easing:'galleria',extend: function(options){},fullscreenCrop:undef,fullscreenDoubleTap:true,fullscreenTransition:undef,height:0,idleMode:true,idleTime:3000,idleSpeed:200,imageCrop:false,imageMargin:0,imagePan:false,imagePanSmoothness:12,imagePosition:'50%',imageTimeout:undef,initialTransition:undef,keepSource:false,layerFollow:true,lightbox:false,lightboxFadeSpeed:200,lightboxTransitionSpeed:200,linkSourceImages:true,maxScaleRatio:undef,maxVideoSize:undef,minScaleRatio:undef,overlayOpacity:0.85,overlayBackground:'#0b0b0b',pauseOnInteraction:true,popupLinks:false,preload:2,queue:true,responsive:true,show:0,showInfo:true,showCounter:true,showImagenav:true,swipe:true,thumbCrop:true,thumbEventType:'click',thumbFit:true,thumbMargin:0,thumbQuality:'auto',thumbDisplayOrder:true,thumbnails:true,touchTransition:undef,transition:'fade',transitionInitial:undef,transitionSpeed:400,trueFullscreen:true,useCanvas:false,vimeo:{title:0,byline:0,portrait:0,color:'aaaaaa'},wait:5000,width:'auto',youtube:{modestbranding:1,autohide:1,color:'white',hd:1,rel:0,showinfo:0}};this._options.initialTransition=this._options.initialTransition||this._options.transitionInitial;if(options&&options.debug===false){DEBUG=false}
if(options&&typeof options.imageTimeout==='number'){TIMEOUT=options.imageTimeout}
if(options&&typeof options.dummy==='string'){DUMMY=options.dummy}
$(this._target).children().hide();if(Galleria.QUIRK){Galleria.raise('Your page is in Quirks mode, Galleria may not render correctly. Please validate your HTML and add a correct doctype.')}
if(typeof Galleria.theme==='object'){this._init()} else{_pool.push(this)}
return this},_init: function(){var self=this,options=this._options;if(this._initialized){Galleria.raise('Init failed: Gallery instance already initialized.');return this}
this._initialized=true;if(!Galleria.theme){Galleria.raise('Init failed: No theme found.',true);return this}
$.extend(true,options,Galleria.theme.defaults,this._original.options,Galleria.configure.options);(function(can){if(!('getContext' in can)){can=null;return}
_canvas=_canvas||{elem:can,context:can.getContext('2d'),cache:{},length:0}}(doc.createElement('canvas')));this.bind(Galleria.DATA, function(){this._original.data=this._data;this.get('total').innerHTML=this.getDataLength();var $container=this.$('container');if(self._options.height<2){self._userRatio=self._ratio=self._options.height}
var num={width:0,height:0};var testHeight=function(){return self.$('stage').height()};Utils.wait({until: function(){num=self._getWH();$container.width(num.width).height(num.height);return testHeight()&&num.width&&num.height>50},success: function(){self._width=num.width;self._height=num.height;self._ratio=self._ratio||num.height/num.width;if(Galleria.WEBKIT){window.setTimeout( function(){self._run()},1)} else{self._run()}},error: function(){if(testHeight()){Galleria.raise('Could not extract sufficient width/height of the gallery container. Traced measures: width:'+num.width+'px, height: '+num.height+'px.',true)} else{Galleria.raise('Could not extract a stage height from the CSS. Traced height: '+testHeight()+'px.',true)}},timeout:typeof this._options.wait=='number'?this._options.wait:false})});this.append({'info-text':['info-title','info-description'],'info':['info-text'],'image-nav':['image-nav-right','image-nav-left'],'stage':['images','loader','counter','image-nav'],'thumbnails-list':['thumbnails'],'thumbnails-container':['thumb-nav-left','thumbnails-list','thumb-nav-right'],'container':['stage','thumbnails-container','info','tooltip']});Utils.hide(this.$('counter').append(this.get('current'),doc.createTextNode(' / '),this.get('total')));this.setCounter('&#8211;');Utils.hide(self.get('tooltip'));this.$('container').addClass(Galleria.TOUCH?'touch':'notouch');$.each(new Array(2), function(i){var image=new Galleria.Picture();$(image.container).css({position:'absolute',top:0,left:0}).prepend(self._layers[i]=$(Utils.create('galleria-layer')).css({position:'absolute',top:0,left:0,right:0,bottom:0,zIndex:2})[0]);self.$('images').append(image.container);self._controls[i]=image});this.$('images').css({position:'relative',top:0,left:0,width:'100%',height:'100%'});this.$('thumbnails, thumbnails-list').css({overflow:'hidden',position:'relative'});this.$('image-nav-right, image-nav-left').bind('click', function(e){if(options.clicknext){e.stopPropagation()}
if(options.pauseOnInteraction){self.pause()}
var fn=/right/.test(this.className)?'next':'prev';self[fn]()});$.each(['info','counter','image-nav'], function(i,el){if(options['show'+el.substr(0,1).toUpperCase()+el.substr(1).replace(/-/,'')]===false){Utils.moveOut(self.get(el.toLowerCase()))}});this.load();if(!options.keepSource&&!IE){this._target.innerHTML=''}
if(this.get('errors')){this.appendChild('target','errors')}
this.appendChild('target','container');if(options.carousel){var count=0,show=options.show;this.bind(Galleria.THUMBNAIL, function(){this.updateCarousel();if(++count==this.getDataLength()&&typeof show=='number'&&show>0){this._carousel.follow(show)}})}
if(options.responsive){$win.bind('resize', function(){if(!self.isFullscreen()){self.resize()}})}
if(options.swipe){(function(images){var swipeStart=[0,0],swipeStop=[0,0],limitX=30,limitY=100,multi=false,tid=0,data,ev={start:'touchstart',move:'touchmove',stop:'touchend'},getData=function(e){return e.originalEvent.touches?e.originalEvent.touches[0]:e},moveHandler=function(e){if(e.originalEvent.touches&&e.originalEvent.touches.length>1){return}
data=getData(e);swipeStop=[data.pageX,data.pageY];if(!swipeStart[0]){swipeStart=swipeStop}
if(Math.abs(swipeStart[0]-swipeStop[0])>10){e.preventDefault()}},upHandler=function(e){images.unbind(ev.move,moveHandler);if((e.originalEvent.touches&&e.originalEvent.touches.length)||multi){multi=!multi;return}
if(Utils.timestamp()-tid<1000&&Math.abs(swipeStart[0]-swipeStop[0])>limitX&&Math.abs(swipeStart[1]-swipeStop[1])<limitY){e.preventDefault();self[swipeStart[0]>swipeStop[0]?'next':'prev']()}
swipeStart=swipeStop=[0,0]};images.bind(ev.start, function(e){if(e.originalEvent.touches&&e.originalEvent.touches.length>1){return}
data=getData(e);tid=Utils.timestamp();swipeStart=swipeStop=[data.pageX,data.pageY];images.bind(ev.move,moveHandler).one(ev.stop,upHandler)})}(self.$('images')));if(options.fullscreenDoubleTap){this.$('stage').bind('touchstart',(function(){var last,cx,cy,lx,ly,now,getData=function(e){return e.originalEvent.touches?e.originalEvent.touches[0]:e};return function(e){now=Galleria.utils.timestamp();cx=getData(e).pageX;cy=getData(e).pageY;if((now-last<500)&&(cx-lx<20)&&(cy-ly<20)){self.toggleFullscreen();e.preventDefault();self.$('stage').unbind('touchend',arguments.callee);return}
last=now;lx=cx;ly=cy}}()))}}
Utils.optimizeTouch(this.get('container'));$.each(Galleria.on.binds, function(i,bind){if($.inArray(bind.hash,self._binds)==-1){self.bind(bind.type,bind.callback)}});return this},addTimer: function(){this._timer.add.apply(this._timer,Utils.array(arguments));return this},clearTimer: function(){this._timer.clear.apply(this._timer,Utils.array(arguments));return this},_getWH: function(){var $container=this.$('container'),$target=this.$('target'),self=this,num={},arr;$.each(['width','height'], function(i,m){if(self._options[m]&&typeof self._options[m]==='number'){num[m]=self._options[m]} else{arr=[Utils.parseValue($container.css(m)),Utils.parseValue($target.css(m)),$container[m](),$target[m]()];if(!self['_'+m]){arr.splice(arr.length,Utils.parseValue($container.css('min-'+m)),Utils.parseValue($target.css('min-'+m)))}
num[m]=Math.max.apply(Math,arr)}});if(self._userRatio){num.height=num.width * self._userRatio}
return num},_createThumbnails: function(push){this.get('total').innerHTML=this.getDataLength();var src,thumb,data,special,$container,self=this,o=this._options,i=push?this._data.length-push.length:0,chunk=i,thumbchunk=[],loadindex=0,gif=IE<8?'http://upload.wikimedia.org/wikipedia/commons/c/c0/Blank.gif':'data:image/gif;base64,R0lGODlhAQABAPABAP///wAAACH5BAEKAAAALAAAAAABAAEAAAICRAEAOw%3D%3D',active=(function(){var a=self.$('thumbnails').find('.active');if(!a.length){return false}
return a.find('img').attr('src')}()),optval=typeof o.thumbnails==='string'?o.thumbnails.toLowerCase():null,getStyle=function(prop){return doc.defaultView&&doc.defaultView.getComputedStyle?doc.defaultView.getComputedStyle(thumb.container,null)[prop]:$container.css(prop)},fake=function(image,index,container){return function(){$(container).append(image);self.trigger({type:Galleria.THUMBNAIL,thumbTarget:image,index:index,galleriaData:self.getData(index)})}},onThumbEvent=function(e){if(o.pauseOnInteraction){self.pause()}
var index=$(e.currentTarget).data('index');if(self.getIndex()!==index){self.show(index)}
e.preventDefault()},thumbComplete=function(thumb,callback){$(thumb.container).css('visibility','visible');self.trigger({type:Galleria.THUMBNAIL,thumbTarget:thumb.image,index:thumb.data.order,galleriaData:self.getData(thumb.data.order)});if(typeof callback=='function'){callback.call(self,thumb)}},onThumbLoad=function(thumb,callback){thumb.scale({width:thumb.data.width,height:thumb.data.height,crop:o.thumbCrop,margin:o.thumbMargin,canvas:o.useCanvas,complete: function(thumb){var top=['left','top'],arr=['Width','Height'],m,css,data=self.getData(thumb.index),special=data.thumb.split(':');$.each(arr, function(i,measure){m=measure.toLowerCase();if((o.thumbCrop!==true||o.thumbCrop===m)&&o.thumbFit){css={};css[m]=thumb[m];$(thumb.container).css(css);css={};css[top[i]]=0;$(thumb.image).css(css)}
thumb['outer'+measure]=$(thumb.container)['outer'+measure](true)});Utils.toggleQuality(thumb.image,o.thumbQuality===true||(o.thumbQuality==='auto'&&thumb.original.width<thumb.width * 3));if(data.iframe&&special.length==2&&special[0] in _video){_video[special[0]].getThumb(special[1],(function(img){return function(src){img.src=src;thumbComplete(thumb,callback)}}(thumb.image)))} else if(o.thumbDisplayOrder&&!thumb.lazy){$.each(thumbchunk, function(i,th){if(i===loadindex&&th.ready&&!th.displayed){loadindex++;th.displayed=true;thumbComplete(th,callback);return}})} else{thumbComplete(thumb,callback)}}})};if(!push){this._thumbnails=[];this.$('thumbnails').empty()}
for(;this._data[i];i++){data=this._data[i];src=data.thumb||data.image;if((o.thumbnails===true||optval=='lazy')&&(data.thumb||data.image)){thumb=new Galleria.Picture(i);thumb.index=i;thumb.displayed=false;thumb.lazy=false;thumb.video=false;this.$('thumbnails').append(thumb.container);$container=$(thumb.container);$container.css('visibility','hidden');thumb.data={width:Utils.parseValue(getStyle('width')),height:Utils.parseValue(getStyle('height')),order:i,src:src};if(o.thumbFit&&o.thumbCrop!==true){$container.css({width:'auto',height:'auto'})} else{$container.css({width:thumb.data.width,height:thumb.data.height})}
special=src.split(':');if(special.length==2&&special[0] in _video){thumb.video=true;thumb.ready=true;thumb.load(gif,{height:thumb.data.height,width:thumb.data.height*1.25},onThumbLoad)} else if(optval=='lazy'){$container.addClass('lazy');thumb.lazy=true;thumb.load(gif,{height:thumb.data.height,width:thumb.data.width})} else{thumb.load(src,onThumbLoad)}
if(o.preload==='all'){thumb.preload(data.image)}} else if(data.iframe||optval==='empty'||optval==='numbers'){thumb={container:Utils.create('galleria-image'),image:Utils.create('img','span'),ready:true};if(optval==='numbers'){$(thumb.image).text(i+1)}
if(data.iframe){$(thumb.image).addClass('iframe')}
this.$('thumbnails').append(thumb.container);window.setTimeout((fake)(thumb.image,i,thumb.container),50+(i*20))} else{thumb={container:null,image:null}}
$(thumb.container).add(o.keepSource&&o.linkSourceImages?data.original:null).data('index',i).bind(o.thumbEventType,onThumbEvent).data('thumbload',onThumbLoad);if(active===src){$(thumb.container).addClass('active')}
this._thumbnails.push(thumb)}
thumbchunk=this._thumbnails.slice(chunk);return this},lazyLoad: function(index,complete){var arr=index.constructor==Array?index:[index],self=this,thumbnails=this.$('thumbnails').children().filter(function(){return $(this).data('lazy-src')}),loaded=0;$.each(arr, function(i,ind){if(ind>self._thumbnails.length-1){return}
var thumb=self._thumbnails[ind],data=thumb.data,special=data.src.split(':'),callback=function(){if(++loaded==arr.length&&typeof complete=='function'){complete.call(self)}},thumbload=$(thumb.container).data('thumbload');if(thumb.video){thumbload.call(self,thumb,callback)} else{thumb.load(data.src, function(thumb){thumbload.call(self,thumb,callback)})}});return this},lazyLoadChunks: function(size,delay){var len=this.getDataLength(),i=0,n=0,arr=[],temp=[],self=this;delay=delay||0;for(;i<len;i++){temp.push(i);if(++n==size||i==len-1){arr.push(temp);n=0;temp=[]}}
var init=function(wait){var a=arr.shift();if(a){window.setTimeout(function(){self.lazyLoad(a, function(){init(true)})},(delay&&wait)?delay:0)}};init(false);return this},_run: function(){var self=this;self._createThumbnails();Utils.wait({timeout:10000,until: function(){if(Galleria.OPERA){self.$('stage').css('display','inline-block')}
self._stageWidth=self.$('stage').width();self._stageHeight=self.$('stage').height();return(self._stageWidth&&self._stageHeight>50)},success: function(){_galleries.push(self);Utils.show(self.get('counter'));if(self._options.carousel){self._carousel.bindControls()}
if(self._options.autoplay){self.pause();if(typeof self._options.autoplay==='number'){self._playtime=self._options.autoplay}
self._playing=true}
if(self._firstrun){if(self._options.autoplay){self.trigger(Galleria.PLAY)}
if(typeof self._options.show==='number'){self.show(self._options.show)}
return}
self._firstrun=true;if(Galleria.History){Galleria.History.change(function(value){if(isNaN(value)){window.history.go(-1)} else{self.show(value,undef,true)}})}
self.trigger(Galleria.READY);Galleria.theme.init.call(self,self._options);$.each(Galleria.ready.callbacks, function(i,fn){if(typeof fn=='function'){fn.call(self,self._options)}});self._options.extend.call(self,self._options);if(/^[0-9]{1,4}$/.test(HASH)&&Galleria.History){self.show(HASH,undef,true)} else if(self._data[self._options.show]){self.show(self._options.show)}
if(self._options.autoplay){self.trigger(Galleria.PLAY)}},error: function(){Galleria.raise('Stage width or height is too small to show the gallery. Traced measures: width:'+self._stageWidth+'px, height: '+self._stageHeight+'px.',true)}})},load: function(source,selector,config){var self=this,o=this._options;this._data=[];this._thumbnails=[];this.$('thumbnails').empty();if(typeof selector==='function'){config=selector;selector=null}
source=source||o.dataSource;selector=selector||o.dataSelector;config=config||o.dataConfig;if(/^function Object/.test(source.constructor)){source=[source]}
if(source.constructor===Array){if(this.validate(source)){this._data=source} else{Galleria.raise('Load failed: JSON Array not valid.')}} else{selector+=',.video,.iframe';$(source).find(selector).each( function(i,elem){elem=$(elem);var data={},parent=elem.parent(),href=parent.attr('href'),rel=parent.attr('rel');if(href&&(elem[0].nodeName=='IMG'||elem.hasClass('video'))&&_videoTest(href)){data.video=href} else if(href&&elem.hasClass('iframe')){data.iframe=href} else{data.image=data.big=href}
if(rel){data.big=rel}
$.each('big title description link layer'.split(' '), function(i,val){if(elem.data(val)){data[val]=elem.data(val)}});self._data.push($.extend({title:elem.attr('title')||'',thumb:elem.attr('src'),image:elem.attr('src'),big:elem.attr('src'),description:elem.attr('alt')||'',link:elem.attr('longdesc'),original:elem.get(0)},data,config(elem)))})}
if(typeof o.dataSort=='function'){protoArray.sort.call(this._data,o.dataSort)} else if(o.dataSort=='random'){this._data.sort( function(){return Math.round(Math.random())-0.5})}
if(this.getDataLength()){this._parseData().trigger(Galleria.DATA)}
return this},_parseData: function(){var self=this,current;$.each(this._data, function(i,data){current=self._data[i];if('thumb' in data===false){current.thumb=data.image}
if(!'big' in data){current.big=data.image}
if('video' in data){var result=_videoTest(data.video);if(result){current.iframe=_video[result.provider].embed(result.id)+(function(){if(typeof self._options[result.provider]=='object'){var str='?',arr=[];$.each(self._options[result.provider], function(key,val){arr.push(key+'='+val)});if(result.provider=='youtube'){arr=['wmode=opaque'].concat(arr)}
return str+arr.join('&')}
return ''}());delete current.video;if(!('thumb' in current)||!current.thumb){current.thumb=result.provider+':'+result.id}}}});return this},destroy: function(){this.$('target').data('galleria',null);this.$('container').unbind('galleria');this.get('target').innerHTML=this._original.html;this.clearTimer();Utils.removeFromArray(_instances,this);Utils.removeFromArray(_galleries,this);return this},splice: function(){var self=this,args=Utils.array(arguments);window.setTimeout(function(){protoArray.splice.apply(self._data,args);self._parseData()._createThumbnails()},2);return self},push: function(){var self=this,args=Utils.array(arguments);if(args.length==1&&args[0].constructor==Array){args=args[0]}
window.setTimeout(function(){protoArray.push.apply(self._data,args);self._parseData()._createThumbnails(args)},2);return self},_getActive: function(){return this._controls.getActive()},validate: function(data){return true},bind: function(type,fn){type=_patchEvent(type);this.$('container').bind(type,this.proxy(fn));return this},unbind: function(type){type=_patchEvent(type);this.$('container').unbind(type);return this},trigger: function(type){type=typeof type==='object'?$.extend(type,{scope:this}):{type:_patchEvent(type),scope:this};this.$('container').trigger(type);return this},addIdleState: function(elem,styles,from,hide){this._idle.add.apply(this._idle,Utils.array(arguments));return this},removeIdleState: function(elem){this._idle.remove.apply(this._idle,Utils.array(arguments));return this},enterIdleMode: function(){this._idle.hide();return this},exitIdleMode: function(){this._idle.showAll();return this},enterFullscreen: function(callback){this._fullscreen.enter.apply(this,Utils.array(arguments));return this},exitFullscreen: function(callback){this._fullscreen.exit.apply(this,Utils.array(arguments));return this},toggleFullscreen: function(callback){this._fullscreen[this.isFullscreen()?'exit':'enter'].apply(this,Utils.array(arguments));return this},bindTooltip: function(elem,value){this._tooltip.bind.apply(this._tooltip,Utils.array(arguments));return this},defineTooltip: function(elem,value){this._tooltip.define.apply(this._tooltip,Utils.array(arguments));return this},refreshTooltip: function(elem){this._tooltip.show.apply(this._tooltip,Utils.array(arguments));return this},openLightbox: function(){this._lightbox.show.apply(this._lightbox,Utils.array(arguments));return this},closeLightbox: function(){this._lightbox.hide.apply(this._lightbox,Utils.array(arguments));return this},getActiveImage: function(){return this._getActive().image||undef},getActiveThumb: function(){return this._thumbnails[this._active].image||undef},getMousePosition: function(e){return{x:e.pageX-this.$('container').offset().left,y:e.pageY-this.$('container').offset().top}},addPan: function(img){if(this._options.imageCrop===false){return}
img=$(img||this.getActiveImage());var self=this,x=img.width()/2,y=img.height()/2,destX=parseInt(img.css('left'),10),destY=parseInt(img.css('top'),10),curX=destX||0,curY=destY||0,distX=0,distY=0,active=false,ts=Utils.timestamp(),cache=0,move=0,position=function(dist,cur,pos){if(dist>0){move=Math.round(Math.max(dist *-1,Math.min(0,cur)));if(cache!==move){cache=move;if(IE===8){img.parent()['scroll'+pos](move *-1)} else{var css={};css[pos.toLowerCase()]=move;img.css(css)}}}},calculate=function(e){if(Utils.timestamp()-ts<50){return}
active=true;x=self.getMousePosition(e).x;y=self.getMousePosition(e).y},loop=function(e){if(!active){return}
distX=img.width()-self._stageWidth;distY=img.height()-self._stageHeight;destX=x/self._stageWidth * distX *-1;destY=y/self._stageHeight * distY *-1;curX+=(destX-curX)/self._options.imagePanSmoothness;curY+=(destY-curY)/self._options.imagePanSmoothness;position(distY,curY,'Top');position(distX,curX,'Left')};if(IE===8){img.parent().scrollTop(curY *-1).scrollLeft(curX *-1);img.css({top:0,left:0})}
this.$('stage').unbind('mousemove',calculate).bind('mousemove',calculate);this.addTimer('pan'+self._id,loop,50,true);return this},proxy: function(fn,scope){if(typeof fn!=='function'){return F}
scope=scope||this;return function(){return fn.apply(scope,Utils.array(arguments))}},removePan: function(){this.$('stage').unbind('mousemove');this.clearTimer('pan'+this._id);return this},addElement: function(id){var dom=this._dom;$.each(Utils.array(arguments), function(i,blueprint){dom[blueprint]=Utils.create('galleria-'+blueprint)});return this},attachKeyboard: function(map){this._keyboard.attach.apply(this._keyboard,Utils.array(arguments));return this},detachKeyboard: function(){this._keyboard.detach.apply(this._keyboard,Utils.array(arguments));return this},appendChild: function(parentID,childID){this.$(parentID).append(this.get(childID)||childID);return this},prependChild: function(parentID,childID){this.$(parentID).prepend(this.get(childID)||childID);return this},remove: function(elemID){this.$(Utils.array(arguments).join(',')).remove();return this},append: function(data){var i,j;for(i in data){if(data.hasOwnProperty(i)){if(data[i].constructor===Array){for(j=0;data[i][j];j++){this.appendChild(i,data[i][j])}} else{this.appendChild(i,data[i])}}}
return this},_scaleImage: function(image,options){image=image||this._controls.getActive();if(!image){return}
var self=this,complete,scaleLayer=function(img){$(img.container).children(':first').css({top:Math.max(0,Utils.parseValue(img.image.style.top)),left:Math.max(0,Utils.parseValue(img.image.style.left)),width:Utils.parseValue(img.image.width),height:Utils.parseValue(img.image.height)})};options=$.extend({width:this._stageWidth,height:this._stageHeight,crop:this._options.imageCrop,max:this._options.maxScaleRatio,min:this._options.minScaleRatio,margin:this._options.imageMargin,position:this._options.imagePosition,iframelimit:this._options.maxVideoSize},options);if(this._options.layerFollow&&this._options.imageCrop!==true){if(typeof options.complete=='function'){complete=options.complete;options.complete=function(){complete.call(image,image);scaleLayer(image)}} else{options.complete=scaleLayer}} else{$(image.container).children(':first').css({top:0,left:0})}
image.scale(options);return this},updateCarousel: function(){this._carousel.update();return this},resize: function(measures,complete){if(typeof measures=='function'){complete=measures;measures=undef}
measures=$.extend({width:0,height:0},measures);var self=this,$container=this.$('container');$.each(measures, function(m,val){if(!val){$container[m]('auto');measures[m]=self._getWH()[m]}});$.each(measures, function(m,val){$container[m](val)});return this.rescale(complete)},rescale: function(width,height,complete){var self=this;if(typeof width==='function'){complete=width;width=undef}
var scale=function(){self._stageWidth=width||self.$('stage').width();self._stageHeight=height||self.$('stage').height();self._scaleImage();if(self._options.carousel){self.updateCarousel()}
self.trigger(Galleria.RESCALE);if(typeof complete==='function'){complete.call(self)}};scale.call(self);return this},refreshImage: function(){this._scaleImage();if(this._options.imagePan){this.addPan()}
return this},show: function(index,rewind,_history){if(this._queue.length>3||index===false||(!this._options.queue&&this._queue.stalled)){return}
index=Math.max(0,Math.min(parseInt(index,10),this.getDataLength()-1));rewind=typeof rewind!=='undefined'?!!rewind:index<this.getIndex();_history=_history||false;if(!_history&&Galleria.History){Galleria.History.set(index.toString());return}
this._active=index;protoArray.push.call(this._queue,{index:index,rewind:rewind});if(!this._queue.stalled){this._show()}
return this},_show: function(){var self=this,queue=this._queue[0],data=this.getData(queue.index);if(!data){return}
var src=data.iframe||(this.isFullscreen()&&'big' in data?data.big:data.image),active=this._controls.getActive(),next=this._controls.getNext(),cached=next.isCached(src),thumb=this._thumbnails[queue.index],mousetrigger=function(){$(next.image).trigger('mouseup')};var complete=(function(data,next,active,queue,thumb){return function(){var win;_transitions.active=false;Utils.toggleQuality(next.image,self._options.imageQuality);self._layers[self._controls.active].innerHTML='';$(active.container).css({zIndex:0,opacity:0}).show();if(active.isIframe){$(active.container).find('iframe').remove()}
self.$('container').toggleClass('iframe',!!data.iframe);$(next.container).css({zIndex:1,left:0,top:0}).show();self._controls.swap();if(self._options.imagePan){self.addPan(next.image)}
if(data.link||self._options.lightbox||self._options.clicknext){$(next.image).css({cursor:'pointer'}).bind('mouseup', function(e){if(typeof e.which=='number'&&e.which>1){return}
if(self._options.clicknext&&!Galleria.TOUCH){if(self._options.pauseOnInteraction){self.pause()}
self.next();return}
if(data.link){if(self._options.popupLinks){win=window.open(data.link,'_blank')} else{window.location.href=data.link}
return}
if(self._options.lightbox){self.openLightbox()}})}
self._playCheck();self.trigger({type:Galleria.IMAGE,index:queue.index,imageTarget:next.image,thumbTarget:thumb.image,galleriaData:data});protoArray.shift.call(self._queue);self._queue.stalled=false;if(self._queue.length){self._show()}}}(data,next,active,queue,thumb));if(this._options.carousel&&this._options.carouselFollow){this._carousel.follow(queue.index)}
if(this._options.preload){var p,i,n=this.getNext(),ndata;try{for(i=this._options.preload;i>0;i--){p=new Galleria.Picture();ndata=self.getData(n);p.preload(this.isFullscreen()&&'big' in ndata?ndata.big:ndata.image);n=self.getNext(n)}} catch(e){}}
Utils.show(next.container);next.isIframe=!!data.iframe;$(self._thumbnails[queue.index].container).addClass('active').siblings('.active').removeClass('active');self.trigger({type:Galleria.LOADSTART,cached:cached,index:queue.index,rewind:queue.rewind,imageTarget:next.image,thumbTarget:thumb.image,galleriaData:data});self._queue.stalled=true;next.load(src, function(next){var layer=$(self._layers[1-self._controls.active]).html(data.layer||'').hide();self._scaleImage(next,{complete: function(next){if('image' in active){Utils.toggleQuality(active.image,false)}
Utils.toggleQuality(next.image,false);self.removePan();self.setInfo(queue.index);self.setCounter(queue.index);if(data.layer){layer.show();if(data.link||self._options.lightbox||self._options.clicknext){layer.css('cursor','pointer').unbind('mouseup').mouseup(mousetrigger)}}
var transition=self._options.transition;$.each({initial:active.image===null,touch:Galleria.TOUCH,fullscreen:self.isFullscreen()}, function(type,arg){if(arg&&self._options[type+'Transition']!==undef){transition=self._options[type+'Transition'];return false}});if(transition in _transitions.effects===false){complete()} else{var params={prev:active.container,next:next.container,rewind:queue.rewind,speed:self._options.transitionSpeed||400};_transitions.active=true;_transitions.init.call(self,transition,params,complete)}
self.trigger({type:Galleria.LOADFINISH,cached:cached,index:queue.index,rewind:queue.rewind,imageTarget:next.image,thumbTarget:self._thumbnails[queue.index].image,galleriaData:self.getData(queue.index)})}})})},getNext: function(base){base=typeof base==='number'?base:this.getIndex();return base===this.getDataLength()-1?0:base+1},getPrev: function(base){base=typeof base==='number'?base:this.getIndex();return base===0?this.getDataLength()-1:base-1},next: function(){if(this.getDataLength()>1){this.show(this.getNext(),false)}
return this},prev: function(){if(this.getDataLength()>1){this.show(this.getPrev(),true)}
return this},get: function(elemId){return elemId in this._dom?this._dom[elemId]:null},getData: function(index){return index in this._data?this._data[index]:this._data[this._active]},getDataLength: function(){return this._data.length},getIndex: function(){return typeof this._active==='number'?this._active:false},getStageHeight: function(){return this._stageHeight},getStageWidth: function(){return this._stageWidth},getOptions: function(key){return typeof key==='undefined'?this._options:this._options[key]},setOptions: function(key,value){if(typeof key==='object'){$.extend(this._options,key)} else{this._options[key]=value}
return this},play: function(delay){this._playing=true;this._playtime=delay||this._playtime;this._playCheck();this.trigger(Galleria.PLAY);return this},pause: function(){this._playing=false;this.trigger(Galleria.PAUSE);return this},playToggle: function(delay){return(this._playing)?this.pause():this.play(delay)},isPlaying: function(){return this._playing},isFullscreen: function(){return this._fullscreen.active},_playCheck: function(){var self=this,played=0,interval=20,now=Utils.timestamp(),timer_id='play'+this._id;if(this._playing){this.clearTimer(timer_id);var fn=function(){played=Utils.timestamp()-now;if(played>=self._playtime&&self._playing){self.clearTimer(timer_id);self.next();return}
if(self._playing){self.trigger({type:Galleria.PROGRESS,percent:Math.ceil(played/self._playtime * 100),seconds:Math.floor(played/1000),milliseconds:played});self.addTimer(timer_id,fn,interval)}};self.addTimer(timer_id,fn,interval)}},setPlaytime: function(delay){this._playtime=delay;return this},setIndex: function(val){this._active=val;return this},setCounter: function(index){if(typeof index==='number'){index++} else if(typeof index==='undefined'){index=this.getIndex()+1}
this.get('current').innerHTML=index;if(IE){var count=this.$('counter'),opacity=count.css('opacity');if(parseInt(opacity,10)===1){Utils.removeAlpha(count[0])} else{this.$('counter').css('opacity',opacity)}}
return this},setInfo: function(index){var self=this,data=this.getData(index);$.each(['title','description'], function(i,type){var elem=self.$('info-'+type);if(!!data[type]){elem[data[type].length?'show':'hide']().html(data[type])} else{elem.empty().hide()}});return this},hasInfo: function(index){var check='title description'.split(' '),i;for(i=0;check[i];i++){if(!!this.getData(index)[check[i]]){return true}}
return false},jQuery: function(str){var self=this,ret=[];$.each(str.split(','), function(i,elemId){elemId=$.trim(elemId);if(self.get(elemId)){ret.push(elemId)}});var jQ=$(self.get(ret.shift()));$.each(ret, function(i,elemId){jQ=jQ.add(self.get(elemId))});return jQ},$: function(str){return this.jQuery.apply(this,Utils.array(arguments))}};$.each(_events, function(i,ev){var type=/_/.test(ev)?ev.replace(/_/g,''):ev;Galleria[ev.toUpperCase()]='galleria.'+type});$.extend(Galleria,{IE9:IE===9,IE8:IE===8,IE7:IE===7,IE6:IE===6,IE:IE,WEBKIT:/webkit/.test(NAV),CHROME:/chrome/.test(NAV),SAFARI:/safari/.test(NAV)&&!(/chrome/.test(NAV)),QUIRK:(IE&&doc.compatMode&&doc.compatMode==="BackCompat"),MAC:/mac/.test(navigator.platform.toLowerCase()),OPERA:!!window.opera,IPHONE:/iphone/.test(NAV),IPAD:/ipad/.test(NAV),ANDROID:/android/.test(NAV),TOUCH:('ontouchstart' in doc)});Galleria.addTheme=function(theme){if(!theme.name){Galleria.raise('No theme name specified')}
if(typeof theme.defaults!=='object'){theme.defaults={}} else{theme.defaults=_legacyOptions(theme.defaults)}
var css=false,reg;if(typeof theme.css==='string'){$('link').each(function(i,link){reg=new RegExp(theme.css.replace('\+\+resource\+\+','\\+\\+resource\\+\\+'));if(reg.test(link.href)){css=true;_themeLoad(theme);return false}});if(!css){$('script').each(function(i,script){reg=new RegExp('galleria\\.'+theme.name.toLowerCase()+'\\.');if(reg.test(script.src)){css=script.src.replace(/[^\/]*$/,'')+theme.css;window.setTimeout(function(){Utils.loadCSS(css,'galleria-theme', function(){_themeLoad(theme)})},1)}})}
if(!css){Galleria.raise('No theme CSS loaded')}} else{_themeLoad(theme)}
return theme};Galleria.loadTheme=function(src,options){if($('script').filter(function(){return $(this).attr('src')==src}).length){return}
var loaded=false,err;$(window).load( function(){if(!loaded){err=window.setTimeout(function(){if(!loaded&&!Galleria.theme){Galleria.raise("Galleria had problems loading theme at "+src+". Please check theme path or load manually.",true)}},20000)}});Galleria.unloadTheme();Utils.loadScript(src, function(){loaded=true;window.clearTimeout(err)});return Galleria};Galleria.unloadTheme=function(){if(typeof Galleria.theme=='object'){$('script').each(function(i,script){if(new RegExp('galleria\\.'+Galleria.theme.name+'\\.').test(script.src)){$(script).remove()}});Galleria.theme=undef}
return Galleria};Galleria.get=function(index){if(!!_instances[index]){return _instances[index]} else if(typeof index!=='number'){return _instances} else{Galleria.raise('Gallery index '+index+' not found')}};Galleria.configure=function(key,value){var opts={};if(typeof key=='string'&&value){opts[key]=value;key=opts} else{$.extend(opts,key)}
Galleria.configure.options=opts;$.each(Galleria.get(), function(i,instance){instance.setOptions(opts)});return Galleria};Galleria.configure.options={};Galleria.on=function(type,callback){if(!type){return}
callback=callback||F;var hash=type+callback.toString().replace(/\s/g,'')+Utils.timestamp();$.each(Galleria.get(), function(i,instance){instance._binds.push(hash);instance.bind(type,callback)});Galleria.on.binds.push({type:type,callback:callback,hash:hash});return Galleria};Galleria.on.binds=[];Galleria.run=function(selector,options){if($.isFunction(options)){options={extend:options}}
$(selector||'#galleria').galleria(options);return Galleria};Galleria.addTransition=function(name,fn){_transitions.effects[name]=fn;return Galleria};Galleria.utils=Utils;Galleria.log=function(){var args=Utils.array(arguments);if('console' in window&&'log' in window.console){try{return window.console.log.apply(window.console,args)} catch(e){$.each(args, function(){window.console.log(this)})}} else{return window.alert(args.join('<br>'))}};Galleria.ready=function(fn){if(typeof fn!='function'){return Galleria}
$.each(_galleries, function(i,gallery){fn.call(gallery,gallery._options)});Galleria.ready.callbacks.push(fn);return Galleria};Galleria.ready.callbacks=[];Galleria.raise=function(msg,fatal){var type=fatal?'Fatal error':'Error',self=this,css={color:'#fff',position:'absolute',top:0,left:0,zIndex:100000},echo=function(msg){var html='<div style="padding:4px;margin:0 0 2px;background:#'+(fatal?'811':'222')+';">'+(fatal?'<strong>'+type+': </strong>':'')+msg+'</div>';$.each(_instances, function(){var cont=this.$('errors'),target=this.$('target');if(!cont.length){target.css('position','relative');cont=this.addElement('errors').appendChild('target','errors').$('errors').css(css)}
cont.append(html)});if(!_instances.length){$('<div>').css($.extend(css,{position:'fixed'})).append(html).appendTo(DOM().body)}};if(DEBUG){echo(msg);if(fatal){throw new Error(type+': '+msg)}} else if(fatal){if(_hasError){return}
_hasError=true;fatal=false;echo('Gallery could not load.')}};Galleria.version=VERSION;Galleria.requires=function(version,msg){msg=msg||'You need to upgrade Galleria to version '+version+' to use one or more components.';if(Galleria.version<version){Galleria.raise(msg,true)}
return Galleria};Galleria.Picture=function(id){this.id=id||null;this.image=null;this.container=Utils.create('galleria-image');$(this.container).css({overflow:'hidden',position:'relative'});this.original={width:0,height:0};this.ready=false;this.isIframe=false};Galleria.Picture.prototype={cache:{},show: function(){Utils.show(this.image)},hide: function(){Utils.moveOut(this.image)},clear: function(){this.image=null},isCached: function(src){return!!this.cache[src]},preload: function(src){$(new Image()).load((function(src,cache){return function(){cache[src]=src}}(src,this.cache))).attr('src',src)},load: function(src,size,callback){if(typeof size=='function'){callback=size;size=null}
if(this.isIframe){var id='if'+new Date().getTime();this.image=$('<iframe>',{src:src,frameborder:0,id:id,allowfullscreen:true,css:{visibility:'hidden'}})[0];$(this.container).find('iframe,img').remove();this.container.appendChild(this.image);$('#'+id).load((function(self,callback){return function(){window.setTimeout(function(){$(self.image).css('visibility','visible');if(typeof callback=='function'){callback.call(self,self)}},10)}}(this,callback)));return this.container}
this.image=new Image();if(Galleria.IE8){$(this.image).css('filter','inherit')}
var i=0,reload=false,resort=false,$container=$(this.container),$image=$(this.image),onerror=function(){if(!reload){reload=true;window.setTimeout((function(image,src){return function(){image.attr('src',src+'?'+Utils.timestamp())}}($(this),src)),50)} else{if(DUMMY){$(this).attr('src',DUMMY)} else{Galleria.raise('Image not found: '+src)}}},onload=(function(self,callback,src){return function(){var complete=function(){$(this).unbind('load');self.original=size||{height:this.height,width:this.width};self.container.appendChild(this);self.cache[src]=src;if(typeof callback=='function'){window.setTimeout(function(){callback.call(self,self)},1)}};if((!this.width||!this.height)){window.setTimeout((function(img){return function(){if(img.width&&img.height){complete.call(img)} else{if(!resort){$(new Image()).load(onload).attr('src',img.src);resort=true} else{Galleria.raise('Could not extract width/height from image: '+img.src+'. Traced measures: width:'+img.width+'px, height: '+img.height+'px.')}}}}(this)),2)} else{complete.call(this)}}}(this,callback,src));$container.find('iframe,img').remove();$image.css('display','block');Utils.hide(this.image);$.each('minWidth minHeight maxWidth maxHeight'.split(' '), function(i,prop){$image.css(prop,(/min/.test(prop)?'0':'none'))});$image.load(onload).error(onerror).attr('src',src);return this.container},scale: function(options){var self=this;options=$.extend({width:0,height:0,min:undef,max:undef,margin:0,complete:F,position:'center',crop:false,canvas:false,iframelimit:undef},options);if(this.isIframe){var cw=options.width,ch=options.height,nw,nh;if(options.iframelimit){var r=Math.min(options.iframelimit/cw,options.iframelimit/ch);if(r<1){nw=cw * r;nh=ch * r;$(this.image).css({top:ch/2-nh/2,left:cw/2-nw/2,position:'absolute'})} else{$(this.image).css({top:0,left:0})}}
$(this.image).width(nw||cw).height(nh||ch).removeAttr('width').removeAttr('height');$(this.container).width(cw).height(ch);options.complete.call(self,self);try{if(this.image.contentWindow){$(this.image.contentWindow).trigger('resize')}} catch(e){}
return this.container}
if(!this.image){return this.container}
var width,height,$container=$(self.container),data;Utils.wait({until: function(){width=options.width||$container.width()||Utils.parseValue($container.css('width'));height=options.height||$container.height()||Utils.parseValue($container.css('height'));return width&&height},success: function(){var newWidth=(width-options.margin * 2)/self.original.width,newHeight=(height-options.margin * 2)/self.original.height,min=Math.min(newWidth,newHeight),max=Math.max(newWidth,newHeight),cropMap={'true':max,'width':newWidth,'height':newHeight,'false':min,'landscape':self.original.width>self.original.height?max:min,'portrait':self.original.width<self.original.height?max:min},ratio=cropMap[options.crop.toString()],canvasKey='';if(options.max){ratio=Math.min(options.max,ratio)}
if(options.min){ratio=Math.max(options.min,ratio)}
$.each(['width','height'], function(i,m){$(self.image)[m](self[m]=self.image[m]=Math.round(self.original[m] * ratio))});$(self.container).width(width).height(height);if(options.canvas&&_canvas){_canvas.elem.width=self.width;_canvas.elem.height=self.height;canvasKey=self.image.src+':'+self.width+'x'+self.height;self.image.src=_canvas.cache[canvasKey]||(function(key){_canvas.context.drawImage(self.image,0,0,self.original.width*ratio,self.original.height*ratio);try{data=_canvas.elem.toDataURL();_canvas.length+=data.length;_canvas.cache[key]=data;return data} catch(e){return self.image.src}}(canvasKey))}
var pos={},mix={},getPosition=function(value,measure,margin){var result=0;if (/\%/.test(value)){var flt=parseInt(value,10)/100,m=self.image[measure]||$(self.image)[measure]();result=Math.ceil(m *-1 * flt+margin * flt)} else{result=Utils.parseValue(value)}
return result},positionMap={'top':{top:0},'left':{left:0},'right':{left:'100%'},'bottom':{top:'100%'}};$.each(options.position.toLowerCase().split(' '), function(i,value){if(value==='center'){value='50%'}
pos[i?'top':'left']=value});$.each(pos, function(i,value){if(positionMap.hasOwnProperty(value)){$.extend(mix,positionMap[value])}});pos=pos.top?$.extend(pos,mix):mix;pos=$.extend({top:'50%',left:'50%'},pos);$(self.image).css({position:'absolute',top:getPosition(pos.top,'height',height),left:getPosition(pos.left,'width',width)});self.show();self.ready=true;options.complete.call(self,self)},error: function(){Galleria.raise('Could not scale image: '+self.image.src)},timeout:1000});return this}};$.extend($.easing,{galleria: function(_,t,b,c,d){if((t/=d/2)<1){return c/2*t*t*t+b}
return c/2*((t-=2)*t*t+2)+b},galleriaIn: function(_,t,b,c,d){return c*(t/=d)*t+b},galleriaOut: function(_,t,b,c,d){return-c *(t/=d)*(t-2)+b}});$.fn.galleria=function(options){var selector=this.selector;if(!$(this).length){$(function(){if($(selector).length){$(selector).galleria(options)} else{Galleria.utils.wait({until: function(){return $(selector).length},success: function(){$(selector).galleria(options)},error: function(){Galleria.raise('Init failed: Galleria could not find the element "'+selector+'".')},timeout:5000})}});return this}
return this.each(function(){if($.data(this,'galleria')){$.data(this,'galleria').destroy();$(this).find('*').hide()}
$.data(this,'galleria',new Galleria().init(this,options))})}}(jQuery));

/* - ++resource++collective.js.bootstrap/js/bootstrap.min.js - */
/*!
 * Bootstrap v3.3.5 (http://getbootstrap.com)
 * Copyright 2011-2015 Twitter, Inc.
 * Licensed under the MIT license
 */
if("undefined"==typeof jQuery)throw new Error("Bootstrap's JavaScript requires jQuery");+function(a){"use strict";var b=a.fn.jquery.split(" ")[0].split(".");if(b[0]<2&&b[1]<9||1==b[0]&&9==b[1]&&b[2]<1)throw new Error("Bootstrap's JavaScript requires jQuery version 1.9.1 or higher")}(jQuery),+function(a){"use strict";function b(){var a=document.createElement("bootstrap"),b={WebkitTransition:"webkitTransitionEnd",MozTransition:"transitionend",OTransition:"oTransitionEnd otransitionend",transition:"transitionend"};for(var c in b)if(void 0!==a.style[c])return{end:b[c]};return!1}a.fn.emulateTransitionEnd=function(b){var c=!1,d=this;a(this).one("bsTransitionEnd",function(){c=!0});var e=function(){c||a(d).trigger(a.support.transition.end)};return setTimeout(e,b),this},a(function(){a.support.transition=b(),a.support.transition&&(a.event.special.bsTransitionEnd={bindType:a.support.transition.end,delegateType:a.support.transition.end,handle:function(b){return a(b.target).is(this)?b.handleObj.handler.apply(this,arguments):void 0}})})}(jQuery),+function(a){"use strict";function b(b){return this.each(function(){var c=a(this),e=c.data("bs.alert");e||c.data("bs.alert",e=new d(this)),"string"==typeof b&&e[b].call(c)})}var c='[data-dismiss="alert"]',d=function(b){a(b).on("click",c,this.close)};d.VERSION="3.3.5",d.TRANSITION_DURATION=150,d.prototype.close=function(b){function c(){g.detach().trigger("closed.bs.alert").remove()}var e=a(this),f=e.attr("data-target");f||(f=e.attr("href"),f=f&&f.replace(/.*(?=#[^\s]*$)/,""));var g=a(f);b&&b.preventDefault(),g.length||(g=e.closest(".alert")),g.trigger(b=a.Event("close.bs.alert")),b.isDefaultPrevented()||(g.removeClass("in"),a.support.transition&&g.hasClass("fade")?g.one("bsTransitionEnd",c).emulateTransitionEnd(d.TRANSITION_DURATION):c())};var e=a.fn.alert;a.fn.alert=b,a.fn.alert.Constructor=d,a.fn.alert.noConflict=function(){return a.fn.alert=e,this},a(document).on("click.bs.alert.data-api",c,d.prototype.close)}(jQuery),+function(a){"use strict";function b(b){return this.each(function(){var d=a(this),e=d.data("bs.button"),f="object"==typeof b&&b;e||d.data("bs.button",e=new c(this,f)),"toggle"==b?e.toggle():b&&e.setState(b)})}var c=function(b,d){this.$element=a(b),this.options=a.extend({},c.DEFAULTS,d),this.isLoading=!1};c.VERSION="3.3.5",c.DEFAULTS={loadingText:"loading..."},c.prototype.setState=function(b){var c="disabled",d=this.$element,e=d.is("input")?"val":"html",f=d.data();b+="Text",null==f.resetText&&d.data("resetText",d[e]()),setTimeout(a.proxy(function(){d[e](null==f[b]?this.options[b]:f[b]),"loadingText"==b?(this.isLoading=!0,d.addClass(c).attr(c,c)):this.isLoading&&(this.isLoading=!1,d.removeClass(c).removeAttr(c))},this),0)},c.prototype.toggle=function(){var a=!0,b=this.$element.closest('[data-toggle="buttons"]');if(b.length){var c=this.$element.find("input");"radio"==c.prop("type")?(c.prop("checked")&&(a=!1),b.find(".active").removeClass("active"),this.$element.addClass("active")):"checkbox"==c.prop("type")&&(c.prop("checked")!==this.$element.hasClass("active")&&(a=!1),this.$element.toggleClass("active")),c.prop("checked",this.$element.hasClass("active")),a&&c.trigger("change")}else this.$element.attr("aria-pressed",!this.$element.hasClass("active")),this.$element.toggleClass("active")};var d=a.fn.button;a.fn.button=b,a.fn.button.Constructor=c,a.fn.button.noConflict=function(){return a.fn.button=d,this},a(document).on("click.bs.button.data-api",'[data-toggle^="button"]',function(c){var d=a(c.target);d.hasClass("btn")||(d=d.closest(".btn")),b.call(d,"toggle"),a(c.target).is('input[type="radio"]')||a(c.target).is('input[type="checkbox"]')||c.preventDefault()}).on("focus.bs.button.data-api blur.bs.button.data-api",'[data-toggle^="button"]',function(b){a(b.target).closest(".btn").toggleClass("focus",/^focus(in)?$/.test(b.type))})}(jQuery),+function(a){"use strict";function b(b){return this.each(function(){var d=a(this),e=d.data("bs.carousel"),f=a.extend({},c.DEFAULTS,d.data(),"object"==typeof b&&b),g="string"==typeof b?b:f.slide;e||d.data("bs.carousel",e=new c(this,f)),"number"==typeof b?e.to(b):g?e[g]():f.interval&&e.pause().cycle()})}var c=function(b,c){this.$element=a(b),this.$indicators=this.$element.find(".carousel-indicators"),this.options=c,this.paused=null,this.sliding=null,this.interval=null,this.$active=null,this.$items=null,this.options.keyboard&&this.$element.on("keydown.bs.carousel",a.proxy(this.keydown,this)),"hover"==this.options.pause&&!("ontouchstart"in document.documentElement)&&this.$element.on("mouseenter.bs.carousel",a.proxy(this.pause,this)).on("mouseleave.bs.carousel",a.proxy(this.cycle,this))};c.VERSION="3.3.5",c.TRANSITION_DURATION=600,c.DEFAULTS={interval:5e3,pause:"hover",wrap:!0,keyboard:!0},c.prototype.keydown=function(a){if(!/input|textarea/i.test(a.target.tagName)){switch(a.which){case 37:this.prev();break;case 39:this.next();break;default:return}a.preventDefault()}},c.prototype.cycle=function(b){return b||(this.paused=!1),this.interval&&clearInterval(this.interval),this.options.interval&&!this.paused&&(this.interval=setInterval(a.proxy(this.next,this),this.options.interval)),this},c.prototype.getItemIndex=function(a){return this.$items=a.parent().children(".item"),this.$items.index(a||this.$active)},c.prototype.getItemForDirection=function(a,b){var c=this.getItemIndex(b),d="prev"==a&&0===c||"next"==a&&c==this.$items.length-1;if(d&&!this.options.wrap)return b;var e="prev"==a?-1:1,f=(c+e)%this.$items.length;return this.$items.eq(f)},c.prototype.to=function(a){var b=this,c=this.getItemIndex(this.$active=this.$element.find(".item.active"));return a>this.$items.length-1||0>a?void 0:this.sliding?this.$element.one("slid.bs.carousel",function(){b.to(a)}):c==a?this.pause().cycle():this.slide(a>c?"next":"prev",this.$items.eq(a))},c.prototype.pause=function(b){return b||(this.paused=!0),this.$element.find(".next, .prev").length&&a.support.transition&&(this.$element.trigger(a.support.transition.end),this.cycle(!0)),this.interval=clearInterval(this.interval),this},c.prototype.next=function(){return this.sliding?void 0:this.slide("next")},c.prototype.prev=function(){return this.sliding?void 0:this.slide("prev")},c.prototype.slide=function(b,d){var e=this.$element.find(".item.active"),f=d||this.getItemForDirection(b,e),g=this.interval,h="next"==b?"left":"right",i=this;if(f.hasClass("active"))return this.sliding=!1;var j=f[0],k=a.Event("slide.bs.carousel",{relatedTarget:j,direction:h});if(this.$element.trigger(k),!k.isDefaultPrevented()){if(this.sliding=!0,g&&this.pause(),this.$indicators.length){this.$indicators.find(".active").removeClass("active");var l=a(this.$indicators.children()[this.getItemIndex(f)]);l&&l.addClass("active")}var m=a.Event("slid.bs.carousel",{relatedTarget:j,direction:h});return a.support.transition&&this.$element.hasClass("slide")?(f.addClass(b),f[0].offsetWidth,e.addClass(h),f.addClass(h),e.one("bsTransitionEnd",function(){f.removeClass([b,h].join(" ")).addClass("active"),e.removeClass(["active",h].join(" ")),i.sliding=!1,setTimeout(function(){i.$element.trigger(m)},0)}).emulateTransitionEnd(c.TRANSITION_DURATION)):(e.removeClass("active"),f.addClass("active"),this.sliding=!1,this.$element.trigger(m)),g&&this.cycle(),this}};var d=a.fn.carousel;a.fn.carousel=b,a.fn.carousel.Constructor=c,a.fn.carousel.noConflict=function(){return a.fn.carousel=d,this};var e=function(c){var d,e=a(this),f=a(e.attr("data-target")||(d=e.attr("href"))&&d.replace(/.*(?=#[^\s]+$)/,""));if(f.hasClass("carousel")){var g=a.extend({},f.data(),e.data()),h=e.attr("data-slide-to");h&&(g.interval=!1),b.call(f,g),h&&f.data("bs.carousel").to(h),c.preventDefault()}};a(document).on("click.bs.carousel.data-api","[data-slide]",e).on("click.bs.carousel.data-api","[data-slide-to]",e),a(window).on("load",function(){a('[data-ride="carousel"]').each(function(){var c=a(this);b.call(c,c.data())})})}(jQuery),+function(a){"use strict";function b(b){var c,d=b.attr("data-target")||(c=b.attr("href"))&&c.replace(/.*(?=#[^\s]+$)/,"");return a(d)}function c(b){return this.each(function(){var c=a(this),e=c.data("bs.collapse"),f=a.extend({},d.DEFAULTS,c.data(),"object"==typeof b&&b);!e&&f.toggle&&/show|hide/.test(b)&&(f.toggle=!1),e||c.data("bs.collapse",e=new d(this,f)),"string"==typeof b&&e[b]()})}var d=function(b,c){this.$element=a(b),this.options=a.extend({},d.DEFAULTS,c),this.$trigger=a('[data-toggle="collapse"][href="#'+b.id+'"],[data-toggle="collapse"][data-target="#'+b.id+'"]'),this.transitioning=null,this.options.parent?this.$parent=this.getParent():this.addAriaAndCollapsedClass(this.$element,this.$trigger),this.options.toggle&&this.toggle()};d.VERSION="3.3.5",d.TRANSITION_DURATION=350,d.DEFAULTS={toggle:!0},d.prototype.dimension=function(){var a=this.$element.hasClass("width");return a?"width":"height"},d.prototype.show=function(){if(!this.transitioning&&!this.$element.hasClass("in")){var b,e=this.$parent&&this.$parent.children(".panel").children(".in, .collapsing");if(!(e&&e.length&&(b=e.data("bs.collapse"),b&&b.transitioning))){var f=a.Event("show.bs.collapse");if(this.$element.trigger(f),!f.isDefaultPrevented()){e&&e.length&&(c.call(e,"hide"),b||e.data("bs.collapse",null));var g=this.dimension();this.$element.removeClass("collapse").addClass("collapsing")[g](0).attr("aria-expanded",!0),this.$trigger.removeClass("collapsed").attr("aria-expanded",!0),this.transitioning=1;var h=function(){this.$element.removeClass("collapsing").addClass("collapse in")[g](""),this.transitioning=0,this.$element.trigger("shown.bs.collapse")};if(!a.support.transition)return h.call(this);var i=a.camelCase(["scroll",g].join("-"));this.$element.one("bsTransitionEnd",a.proxy(h,this)).emulateTransitionEnd(d.TRANSITION_DURATION)[g](this.$element[0][i])}}}},d.prototype.hide=function(){if(!this.transitioning&&this.$element.hasClass("in")){var b=a.Event("hide.bs.collapse");if(this.$element.trigger(b),!b.isDefaultPrevented()){var c=this.dimension();this.$element[c](this.$element[c]())[0].offsetHeight,this.$element.addClass("collapsing").removeClass("collapse in").attr("aria-expanded",!1),this.$trigger.addClass("collapsed").attr("aria-expanded",!1),this.transitioning=1;var e=function(){this.transitioning=0,this.$element.removeClass("collapsing").addClass("collapse").trigger("hidden.bs.collapse")};return a.support.transition?void this.$element[c](0).one("bsTransitionEnd",a.proxy(e,this)).emulateTransitionEnd(d.TRANSITION_DURATION):e.call(this)}}},d.prototype.toggle=function(){this[this.$element.hasClass("in")?"hide":"show"]()},d.prototype.getParent=function(){return a(this.options.parent).find('[data-toggle="collapse"][data-parent="'+this.options.parent+'"]').each(a.proxy(function(c,d){var e=a(d);this.addAriaAndCollapsedClass(b(e),e)},this)).end()},d.prototype.addAriaAndCollapsedClass=function(a,b){var c=a.hasClass("in");a.attr("aria-expanded",c),b.toggleClass("collapsed",!c).attr("aria-expanded",c)};var e=a.fn.collapse;a.fn.collapse=c,a.fn.collapse.Constructor=d,a.fn.collapse.noConflict=function(){return a.fn.collapse=e,this},a(document).on("click.bs.collapse.data-api",'[data-toggle="collapse"]',function(d){var e=a(this);e.attr("data-target")||d.preventDefault();var f=b(e),g=f.data("bs.collapse"),h=g?"toggle":e.data();c.call(f,h)})}(jQuery),+function(a){"use strict";function b(b){var c=b.attr("data-target");c||(c=b.attr("href"),c=c&&/#[A-Za-z]/.test(c)&&c.replace(/.*(?=#[^\s]*$)/,""));var d=c&&a(c);return d&&d.length?d:b.parent()}function c(c){c&&3===c.which||(a(e).remove(),a(f).each(function(){var d=a(this),e=b(d),f={relatedTarget:this};e.hasClass("open")&&(c&&"click"==c.type&&/input|textarea/i.test(c.target.tagName)&&a.contains(e[0],c.target)||(e.trigger(c=a.Event("hide.bs.dropdown",f)),c.isDefaultPrevented()||(d.attr("aria-expanded","false"),e.removeClass("open").trigger("hidden.bs.dropdown",f))))}))}function d(b){return this.each(function(){var c=a(this),d=c.data("bs.dropdown");d||c.data("bs.dropdown",d=new g(this)),"string"==typeof b&&d[b].call(c)})}var e=".dropdown-backdrop",f='[data-toggle="dropdown"]',g=function(b){a(b).on("click.bs.dropdown",this.toggle)};g.VERSION="3.3.5",g.prototype.toggle=function(d){var e=a(this);if(!e.is(".disabled, :disabled")){var f=b(e),g=f.hasClass("open");if(c(),!g){"ontouchstart"in document.documentElement&&!f.closest(".navbar-nav").length&&a(document.createElement("div")).addClass("dropdown-backdrop").insertAfter(a(this)).on("click",c);var h={relatedTarget:this};if(f.trigger(d=a.Event("show.bs.dropdown",h)),d.isDefaultPrevented())return;e.trigger("focus").attr("aria-expanded","true"),f.toggleClass("open").trigger("shown.bs.dropdown",h)}return!1}},g.prototype.keydown=function(c){if(/(38|40|27|32)/.test(c.which)&&!/input|textarea/i.test(c.target.tagName)){var d=a(this);if(c.preventDefault(),c.stopPropagation(),!d.is(".disabled, :disabled")){var e=b(d),g=e.hasClass("open");if(!g&&27!=c.which||g&&27==c.which)return 27==c.which&&e.find(f).trigger("focus"),d.trigger("click");var h=" li:not(.disabled):visible a",i=e.find(".dropdown-menu"+h);if(i.length){var j=i.index(c.target);38==c.which&&j>0&&j--,40==c.which&&j<i.length-1&&j++,~j||(j=0),i.eq(j).trigger("focus")}}}};var h=a.fn.dropdown;a.fn.dropdown=d,a.fn.dropdown.Constructor=g,a.fn.dropdown.noConflict=function(){return a.fn.dropdown=h,this},a(document).on("click.bs.dropdown.data-api",c).on("click.bs.dropdown.data-api",".dropdown form",function(a){a.stopPropagation()}).on("click.bs.dropdown.data-api",f,g.prototype.toggle).on("keydown.bs.dropdown.data-api",f,g.prototype.keydown).on("keydown.bs.dropdown.data-api",".dropdown-menu",g.prototype.keydown)}(jQuery),+function(a){"use strict";function b(b,d){return this.each(function(){var e=a(this),f=e.data("bs.modal"),g=a.extend({},c.DEFAULTS,e.data(),"object"==typeof b&&b);f||e.data("bs.modal",f=new c(this,g)),"string"==typeof b?f[b](d):g.show&&f.show(d)})}var c=function(b,c){this.options=c,this.$body=a(document.body),this.$element=a(b),this.$dialog=this.$element.find(".modal-dialog"),this.$backdrop=null,this.isShown=null,this.originalBodyPad=null,this.scrollbarWidth=0,this.ignoreBackdropClick=!1,this.options.remote&&this.$element.find(".modal-content").load(this.options.remote,a.proxy(function(){this.$element.trigger("loaded.bs.modal")},this))};c.VERSION="3.3.5",c.TRANSITION_DURATION=300,c.BACKDROP_TRANSITION_DURATION=150,c.DEFAULTS={backdrop:!0,keyboard:!0,show:!0},c.prototype.toggle=function(a){return this.isShown?this.hide():this.show(a)},c.prototype.show=function(b){var d=this,e=a.Event("show.bs.modal",{relatedTarget:b});this.$element.trigger(e),this.isShown||e.isDefaultPrevented()||(this.isShown=!0,this.checkScrollbar(),this.setScrollbar(),this.$body.addClass("modal-open"),this.escape(),this.resize(),this.$element.on("click.dismiss.bs.modal",'[data-dismiss="modal"]',a.proxy(this.hide,this)),this.$dialog.on("mousedown.dismiss.bs.modal",function(){d.$element.one("mouseup.dismiss.bs.modal",function(b){a(b.target).is(d.$element)&&(d.ignoreBackdropClick=!0)})}),this.backdrop(function(){var e=a.support.transition&&d.$element.hasClass("fade");d.$element.parent().length||d.$element.appendTo(d.$body),d.$element.show().scrollTop(0),d.adjustDialog(),e&&d.$element[0].offsetWidth,d.$element.addClass("in"),d.enforceFocus();var f=a.Event("shown.bs.modal",{relatedTarget:b});e?d.$dialog.one("bsTransitionEnd",function(){d.$element.trigger("focus").trigger(f)}).emulateTransitionEnd(c.TRANSITION_DURATION):d.$element.trigger("focus").trigger(f)}))},c.prototype.hide=function(b){b&&b.preventDefault(),b=a.Event("hide.bs.modal"),this.$element.trigger(b),this.isShown&&!b.isDefaultPrevented()&&(this.isShown=!1,this.escape(),this.resize(),a(document).off("focusin.bs.modal"),this.$element.removeClass("in").off("click.dismiss.bs.modal").off("mouseup.dismiss.bs.modal"),this.$dialog.off("mousedown.dismiss.bs.modal"),a.support.transition&&this.$element.hasClass("fade")?this.$element.one("bsTransitionEnd",a.proxy(this.hideModal,this)).emulateTransitionEnd(c.TRANSITION_DURATION):this.hideModal())},c.prototype.enforceFocus=function(){a(document).off("focusin.bs.modal").on("focusin.bs.modal",a.proxy(function(a){this.$element[0]===a.target||this.$element.has(a.target).length||this.$element.trigger("focus")},this))},c.prototype.escape=function(){this.isShown&&this.options.keyboard?this.$element.on("keydown.dismiss.bs.modal",a.proxy(function(a){27==a.which&&this.hide()},this)):this.isShown||this.$element.off("keydown.dismiss.bs.modal")},c.prototype.resize=function(){this.isShown?a(window).on("resize.bs.modal",a.proxy(this.handleUpdate,this)):a(window).off("resize.bs.modal")},c.prototype.hideModal=function(){var a=this;this.$element.hide(),this.backdrop(function(){a.$body.removeClass("modal-open"),a.resetAdjustments(),a.resetScrollbar(),a.$element.trigger("hidden.bs.modal")})},c.prototype.removeBackdrop=function(){this.$backdrop&&this.$backdrop.remove(),this.$backdrop=null},c.prototype.backdrop=function(b){var d=this,e=this.$element.hasClass("fade")?"fade":"";if(this.isShown&&this.options.backdrop){var f=a.support.transition&&e;if(this.$backdrop=a(document.createElement("div")).addClass("modal-backdrop "+e).appendTo(this.$body),this.$element.on("click.dismiss.bs.modal",a.proxy(function(a){return this.ignoreBackdropClick?void(this.ignoreBackdropClick=!1):void(a.target===a.currentTarget&&("static"==this.options.backdrop?this.$element[0].focus():this.hide()))},this)),f&&this.$backdrop[0].offsetWidth,this.$backdrop.addClass("in"),!b)return;f?this.$backdrop.one("bsTransitionEnd",b).emulateTransitionEnd(c.BACKDROP_TRANSITION_DURATION):b()}else if(!this.isShown&&this.$backdrop){this.$backdrop.removeClass("in");var g=function(){d.removeBackdrop(),b&&b()};a.support.transition&&this.$element.hasClass("fade")?this.$backdrop.one("bsTransitionEnd",g).emulateTransitionEnd(c.BACKDROP_TRANSITION_DURATION):g()}else b&&b()},c.prototype.handleUpdate=function(){this.adjustDialog()},c.prototype.adjustDialog=function(){var a=this.$element[0].scrollHeight>document.documentElement.clientHeight;this.$element.css({paddingLeft:!this.bodyIsOverflowing&&a?this.scrollbarWidth:"",paddingRight:this.bodyIsOverflowing&&!a?this.scrollbarWidth:""})},c.prototype.resetAdjustments=function(){this.$element.css({paddingLeft:"",paddingRight:""})},c.prototype.checkScrollbar=function(){var a=window.innerWidth;if(!a){var b=document.documentElement.getBoundingClientRect();a=b.right-Math.abs(b.left)}this.bodyIsOverflowing=document.body.clientWidth<a,this.scrollbarWidth=this.measureScrollbar()},c.prototype.setScrollbar=function(){var a=parseInt(this.$body.css("padding-right")||0,10);this.originalBodyPad=document.body.style.paddingRight||"",this.bodyIsOverflowing&&this.$body.css("padding-right",a+this.scrollbarWidth)},c.prototype.resetScrollbar=function(){this.$body.css("padding-right",this.originalBodyPad)},c.prototype.measureScrollbar=function(){var a=document.createElement("div");a.className="modal-scrollbar-measure",this.$body.append(a);var b=a.offsetWidth-a.clientWidth;return this.$body[0].removeChild(a),b};var d=a.fn.modal;a.fn.modal=b,a.fn.modal.Constructor=c,a.fn.modal.noConflict=function(){return a.fn.modal=d,this},a(document).on("click.bs.modal.data-api",'[data-toggle="modal"]',function(c){var d=a(this),e=d.attr("href"),f=a(d.attr("data-target")||e&&e.replace(/.*(?=#[^\s]+$)/,"")),g=f.data("bs.modal")?"toggle":a.extend({remote:!/#/.test(e)&&e},f.data(),d.data());d.is("a")&&c.preventDefault(),f.one("show.bs.modal",function(a){a.isDefaultPrevented()||f.one("hidden.bs.modal",function(){d.is(":visible")&&d.trigger("focus")})}),b.call(f,g,this)})}(jQuery),+function(a){"use strict";function b(b){return this.each(function(){var d=a(this),e=d.data("bs.tooltip"),f="object"==typeof b&&b;(e||!/destroy|hide/.test(b))&&(e||d.data("bs.tooltip",e=new c(this,f)),"string"==typeof b&&e[b]())})}var c=function(a,b){this.type=null,this.options=null,this.enabled=null,this.timeout=null,this.hoverState=null,this.$element=null,this.inState=null,this.init("tooltip",a,b)};c.VERSION="3.3.5",c.TRANSITION_DURATION=150,c.DEFAULTS={animation:!0,placement:"top",selector:!1,template:'<div class="tooltip" role="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>',trigger:"hover focus",title:"",delay:0,html:!1,container:!1,viewport:{selector:"body",padding:0}},c.prototype.init=function(b,c,d){if(this.enabled=!0,this.type=b,this.$element=a(c),this.options=this.getOptions(d),this.$viewport=this.options.viewport&&a(a.isFunction(this.options.viewport)?this.options.viewport.call(this,this.$element):this.options.viewport.selector||this.options.viewport),this.inState={click:!1,hover:!1,focus:!1},this.$element[0]instanceof document.constructor&&!this.options.selector)throw new Error("`selector` option must be specified when initializing "+this.type+" on the window.document object!");for(var e=this.options.trigger.split(" "),f=e.length;f--;){var g=e[f];if("click"==g)this.$element.on("click."+this.type,this.options.selector,a.proxy(this.toggle,this));else if("manual"!=g){var h="hover"==g?"mouseenter":"focusin",i="hover"==g?"mouseleave":"focusout";this.$element.on(h+"."+this.type,this.options.selector,a.proxy(this.enter,this)),this.$element.on(i+"."+this.type,this.options.selector,a.proxy(this.leave,this))}}this.options.selector?this._options=a.extend({},this.options,{trigger:"manual",selector:""}):this.fixTitle()},c.prototype.getDefaults=function(){return c.DEFAULTS},c.prototype.getOptions=function(b){return b=a.extend({},this.getDefaults(),this.$element.data(),b),b.delay&&"number"==typeof b.delay&&(b.delay={show:b.delay,hide:b.delay}),b},c.prototype.getDelegateOptions=function(){var b={},c=this.getDefaults();return this._options&&a.each(this._options,function(a,d){c[a]!=d&&(b[a]=d)}),b},c.prototype.enter=function(b){var c=b instanceof this.constructor?b:a(b.currentTarget).data("bs."+this.type);return c||(c=new this.constructor(b.currentTarget,this.getDelegateOptions()),a(b.currentTarget).data("bs."+this.type,c)),b instanceof a.Event&&(c.inState["focusin"==b.type?"focus":"hover"]=!0),c.tip().hasClass("in")||"in"==c.hoverState?void(c.hoverState="in"):(clearTimeout(c.timeout),c.hoverState="in",c.options.delay&&c.options.delay.show?void(c.timeout=setTimeout(function(){"in"==c.hoverState&&c.show()},c.options.delay.show)):c.show())},c.prototype.isInStateTrue=function(){for(var a in this.inState)if(this.inState[a])return!0;return!1},c.prototype.leave=function(b){var c=b instanceof this.constructor?b:a(b.currentTarget).data("bs."+this.type);return c||(c=new this.constructor(b.currentTarget,this.getDelegateOptions()),a(b.currentTarget).data("bs."+this.type,c)),b instanceof a.Event&&(c.inState["focusout"==b.type?"focus":"hover"]=!1),c.isInStateTrue()?void 0:(clearTimeout(c.timeout),c.hoverState="out",c.options.delay&&c.options.delay.hide?void(c.timeout=setTimeout(function(){"out"==c.hoverState&&c.hide()},c.options.delay.hide)):c.hide())},c.prototype.show=function(){var b=a.Event("show.bs."+this.type);if(this.hasContent()&&this.enabled){this.$element.trigger(b);var d=a.contains(this.$element[0].ownerDocument.documentElement,this.$element[0]);if(b.isDefaultPrevented()||!d)return;var e=this,f=this.tip(),g=this.getUID(this.type);this.setContent(),f.attr("id",g),this.$element.attr("aria-describedby",g),this.options.animation&&f.addClass("fade");var h="function"==typeof this.options.placement?this.options.placement.call(this,f[0],this.$element[0]):this.options.placement,i=/\s?auto?\s?/i,j=i.test(h);j&&(h=h.replace(i,"")||"top"),f.detach().css({top:0,left:0,display:"block"}).addClass(h).data("bs."+this.type,this),this.options.container?f.appendTo(this.options.container):f.insertAfter(this.$element),this.$element.trigger("inserted.bs."+this.type);var k=this.getPosition(),l=f[0].offsetWidth,m=f[0].offsetHeight;if(j){var n=h,o=this.getPosition(this.$viewport);h="bottom"==h&&k.bottom+m>o.bottom?"top":"top"==h&&k.top-m<o.top?"bottom":"right"==h&&k.right+l>o.width?"left":"left"==h&&k.left-l<o.left?"right":h,f.removeClass(n).addClass(h)}var p=this.getCalculatedOffset(h,k,l,m);this.applyPlacement(p,h);var q=function(){var a=e.hoverState;e.$element.trigger("shown.bs."+e.type),e.hoverState=null,"out"==a&&e.leave(e)};a.support.transition&&this.$tip.hasClass("fade")?f.one("bsTransitionEnd",q).emulateTransitionEnd(c.TRANSITION_DURATION):q()}},c.prototype.applyPlacement=function(b,c){var d=this.tip(),e=d[0].offsetWidth,f=d[0].offsetHeight,g=parseInt(d.css("margin-top"),10),h=parseInt(d.css("margin-left"),10);isNaN(g)&&(g=0),isNaN(h)&&(h=0),b.top+=g,b.left+=h,a.offset.setOffset(d[0],a.extend({using:function(a){d.css({top:Math.round(a.top),left:Math.round(a.left)})}},b),0),d.addClass("in");var i=d[0].offsetWidth,j=d[0].offsetHeight;"top"==c&&j!=f&&(b.top=b.top+f-j);var k=this.getViewportAdjustedDelta(c,b,i,j);k.left?b.left+=k.left:b.top+=k.top;var l=/top|bottom/.test(c),m=l?2*k.left-e+i:2*k.top-f+j,n=l?"offsetWidth":"offsetHeight";d.offset(b),this.replaceArrow(m,d[0][n],l)},c.prototype.replaceArrow=function(a,b,c){this.arrow().css(c?"left":"top",50*(1-a/b)+"%").css(c?"top":"left","")},c.prototype.setContent=function(){var a=this.tip(),b=this.getTitle();a.find(".tooltip-inner")[this.options.html?"html":"text"](b),a.removeClass("fade in top bottom left right")},c.prototype.hide=function(b){function d(){"in"!=e.hoverState&&f.detach(),e.$element.removeAttr("aria-describedby").trigger("hidden.bs."+e.type),b&&b()}var e=this,f=a(this.$tip),g=a.Event("hide.bs."+this.type);return this.$element.trigger(g),g.isDefaultPrevented()?void 0:(f.removeClass("in"),a.support.transition&&f.hasClass("fade")?f.one("bsTransitionEnd",d).emulateTransitionEnd(c.TRANSITION_DURATION):d(),this.hoverState=null,this)},c.prototype.fixTitle=function(){var a=this.$element;(a.attr("title")||"string"!=typeof a.attr("data-original-title"))&&a.attr("data-original-title",a.attr("title")||"").attr("title","")},c.prototype.hasContent=function(){return this.getTitle()},c.prototype.getPosition=function(b){b=b||this.$element;var c=b[0],d="BODY"==c.tagName,e=c.getBoundingClientRect();null==e.width&&(e=a.extend({},e,{width:e.right-e.left,height:e.bottom-e.top}));var f=d?{top:0,left:0}:b.offset(),g={scroll:d?document.documentElement.scrollTop||document.body.scrollTop:b.scrollTop()},h=d?{width:a(window).width(),height:a(window).height()}:null;return a.extend({},e,g,h,f)},c.prototype.getCalculatedOffset=function(a,b,c,d){return"bottom"==a?{top:b.top+b.height,left:b.left+b.width/2-c/2}:"top"==a?{top:b.top-d,left:b.left+b.width/2-c/2}:"left"==a?{top:b.top+b.height/2-d/2,left:b.left-c}:{top:b.top+b.height/2-d/2,left:b.left+b.width}},c.prototype.getViewportAdjustedDelta=function(a,b,c,d){var e={top:0,left:0};if(!this.$viewport)return e;var f=this.options.viewport&&this.options.viewport.padding||0,g=this.getPosition(this.$viewport);if(/right|left/.test(a)){var h=b.top-f-g.scroll,i=b.top+f-g.scroll+d;h<g.top?e.top=g.top-h:i>g.top+g.height&&(e.top=g.top+g.height-i)}else{var j=b.left-f,k=b.left+f+c;j<g.left?e.left=g.left-j:k>g.right&&(e.left=g.left+g.width-k)}return e},c.prototype.getTitle=function(){var a,b=this.$element,c=this.options;return a=b.attr("data-original-title")||("function"==typeof c.title?c.title.call(b[0]):c.title)},c.prototype.getUID=function(a){do a+=~~(1e6*Math.random());while(document.getElementById(a));return a},c.prototype.tip=function(){if(!this.$tip&&(this.$tip=a(this.options.template),1!=this.$tip.length))throw new Error(this.type+" `template` option must consist of exactly 1 top-level element!");return this.$tip},c.prototype.arrow=function(){return this.$arrow=this.$arrow||this.tip().find(".tooltip-arrow")},c.prototype.enable=function(){this.enabled=!0},c.prototype.disable=function(){this.enabled=!1},c.prototype.toggleEnabled=function(){this.enabled=!this.enabled},c.prototype.toggle=function(b){var c=this;b&&(c=a(b.currentTarget).data("bs."+this.type),c||(c=new this.constructor(b.currentTarget,this.getDelegateOptions()),a(b.currentTarget).data("bs."+this.type,c))),b?(c.inState.click=!c.inState.click,c.isInStateTrue()?c.enter(c):c.leave(c)):c.tip().hasClass("in")?c.leave(c):c.enter(c)},c.prototype.destroy=function(){var a=this;clearTimeout(this.timeout),this.hide(function(){a.$element.off("."+a.type).removeData("bs."+a.type),a.$tip&&a.$tip.detach(),a.$tip=null,a.$arrow=null,a.$viewport=null})};var d=a.fn.tooltip;a.fn.tooltip=b,a.fn.tooltip.Constructor=c,a.fn.tooltip.noConflict=function(){return a.fn.tooltip=d,this}}(jQuery),+function(a){"use strict";function b(b){return this.each(function(){var d=a(this),e=d.data("bs.popover"),f="object"==typeof b&&b;(e||!/destroy|hide/.test(b))&&(e||d.data("bs.popover",e=new c(this,f)),"string"==typeof b&&e[b]())})}var c=function(a,b){this.init("popover",a,b)};if(!a.fn.tooltip)throw new Error("Popover requires tooltip.js");c.VERSION="3.3.5",c.DEFAULTS=a.extend({},a.fn.tooltip.Constructor.DEFAULTS,{placement:"right",trigger:"click",content:"",template:'<div class="popover" role="tooltip"><div class="arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'}),c.prototype=a.extend({},a.fn.tooltip.Constructor.prototype),c.prototype.constructor=c,c.prototype.getDefaults=function(){return c.DEFAULTS},c.prototype.setContent=function(){var a=this.tip(),b=this.getTitle(),c=this.getContent();a.find(".popover-title")[this.options.html?"html":"text"](b),a.find(".popover-content").children().detach().end()[this.options.html?"string"==typeof c?"html":"append":"text"](c),a.removeClass("fade top bottom left right in"),a.find(".popover-title").html()||a.find(".popover-title").hide()},c.prototype.hasContent=function(){return this.getTitle()||this.getContent()},c.prototype.getContent=function(){var a=this.$element,b=this.options;return a.attr("data-content")||("function"==typeof b.content?b.content.call(a[0]):b.content)},c.prototype.arrow=function(){return this.$arrow=this.$arrow||this.tip().find(".arrow")};var d=a.fn.popover;a.fn.popover=b,a.fn.popover.Constructor=c,a.fn.popover.noConflict=function(){return a.fn.popover=d,this}}(jQuery),+function(a){"use strict";function b(c,d){this.$body=a(document.body),this.$scrollElement=a(a(c).is(document.body)?window:c),this.options=a.extend({},b.DEFAULTS,d),this.selector=(this.options.target||"")+" .nav li > a",this.offsets=[],this.targets=[],this.activeTarget=null,this.scrollHeight=0,this.$scrollElement.on("scroll.bs.scrollspy",a.proxy(this.process,this)),this.refresh(),this.process()}function c(c){return this.each(function(){var d=a(this),e=d.data("bs.scrollspy"),f="object"==typeof c&&c;e||d.data("bs.scrollspy",e=new b(this,f)),"string"==typeof c&&e[c]()})}b.VERSION="3.3.5",b.DEFAULTS={offset:10},b.prototype.getScrollHeight=function(){return this.$scrollElement[0].scrollHeight||Math.max(this.$body[0].scrollHeight,document.documentElement.scrollHeight)},b.prototype.refresh=function(){var b=this,c="offset",d=0;this.offsets=[],this.targets=[],this.scrollHeight=this.getScrollHeight(),a.isWindow(this.$scrollElement[0])||(c="position",d=this.$scrollElement.scrollTop()),this.$body.find(this.selector).map(function(){var b=a(this),e=b.data("target")||b.attr("href"),f=/^#./.test(e)&&a(e);return f&&f.length&&f.is(":visible")&&[[f[c]().top+d,e]]||null}).sort(function(a,b){return a[0]-b[0]}).each(function(){b.offsets.push(this[0]),b.targets.push(this[1])})},b.prototype.process=function(){var a,b=this.$scrollElement.scrollTop()+this.options.offset,c=this.getScrollHeight(),d=this.options.offset+c-this.$scrollElement.height(),e=this.offsets,f=this.targets,g=this.activeTarget;if(this.scrollHeight!=c&&this.refresh(),b>=d)return g!=(a=f[f.length-1])&&this.activate(a);if(g&&b<e[0])return this.activeTarget=null,this.clear();for(a=e.length;a--;)g!=f[a]&&b>=e[a]&&(void 0===e[a+1]||b<e[a+1])&&this.activate(f[a])},b.prototype.activate=function(b){this.activeTarget=b,this.clear();var c=this.selector+'[data-target="'+b+'"],'+this.selector+'[href="'+b+'"]',d=a(c).parents("li").addClass("active");d.parent(".dropdown-menu").length&&(d=d.closest("li.dropdown").addClass("active")),
d.trigger("activate.bs.scrollspy")},b.prototype.clear=function(){a(this.selector).parentsUntil(this.options.target,".active").removeClass("active")};var d=a.fn.scrollspy;a.fn.scrollspy=c,a.fn.scrollspy.Constructor=b,a.fn.scrollspy.noConflict=function(){return a.fn.scrollspy=d,this},a(window).on("load.bs.scrollspy.data-api",function(){a('[data-spy="scroll"]').each(function(){var b=a(this);c.call(b,b.data())})})}(jQuery),+function(a){"use strict";function b(b){return this.each(function(){var d=a(this),e=d.data("bs.tab");e||d.data("bs.tab",e=new c(this)),"string"==typeof b&&e[b]()})}var c=function(b){this.element=a(b)};c.VERSION="3.3.5",c.TRANSITION_DURATION=150,c.prototype.show=function(){var b=this.element,c=b.closest("ul:not(.dropdown-menu)"),d=b.data("target");if(d||(d=b.attr("href"),d=d&&d.replace(/.*(?=#[^\s]*$)/,"")),!b.parent("li").hasClass("active")){var e=c.find(".active:last a"),f=a.Event("hide.bs.tab",{relatedTarget:b[0]}),g=a.Event("show.bs.tab",{relatedTarget:e[0]});if(e.trigger(f),b.trigger(g),!g.isDefaultPrevented()&&!f.isDefaultPrevented()){var h=a(d);this.activate(b.closest("li"),c),this.activate(h,h.parent(),function(){e.trigger({type:"hidden.bs.tab",relatedTarget:b[0]}),b.trigger({type:"shown.bs.tab",relatedTarget:e[0]})})}}},c.prototype.activate=function(b,d,e){function f(){g.removeClass("active").find("> .dropdown-menu > .active").removeClass("active").end().find('[data-toggle="tab"]').attr("aria-expanded",!1),b.addClass("active").find('[data-toggle="tab"]').attr("aria-expanded",!0),h?(b[0].offsetWidth,b.addClass("in")):b.removeClass("fade"),b.parent(".dropdown-menu").length&&b.closest("li.dropdown").addClass("active").end().find('[data-toggle="tab"]').attr("aria-expanded",!0),e&&e()}var g=d.find("> .active"),h=e&&a.support.transition&&(g.length&&g.hasClass("fade")||!!d.find("> .fade").length);g.length&&h?g.one("bsTransitionEnd",f).emulateTransitionEnd(c.TRANSITION_DURATION):f(),g.removeClass("in")};var d=a.fn.tab;a.fn.tab=b,a.fn.tab.Constructor=c,a.fn.tab.noConflict=function(){return a.fn.tab=d,this};var e=function(c){c.preventDefault(),b.call(a(this),"show")};a(document).on("click.bs.tab.data-api",'[data-toggle="tab"]',e).on("click.bs.tab.data-api",'[data-toggle="pill"]',e)}(jQuery),+function(a){"use strict";function b(b){return this.each(function(){var d=a(this),e=d.data("bs.affix"),f="object"==typeof b&&b;e||d.data("bs.affix",e=new c(this,f)),"string"==typeof b&&e[b]()})}var c=function(b,d){this.options=a.extend({},c.DEFAULTS,d),this.$target=a(this.options.target).on("scroll.bs.affix.data-api",a.proxy(this.checkPosition,this)).on("click.bs.affix.data-api",a.proxy(this.checkPositionWithEventLoop,this)),this.$element=a(b),this.affixed=null,this.unpin=null,this.pinnedOffset=null,this.checkPosition()};c.VERSION="3.3.5",c.RESET="affix affix-top affix-bottom",c.DEFAULTS={offset:0,target:window},c.prototype.getState=function(a,b,c,d){var e=this.$target.scrollTop(),f=this.$element.offset(),g=this.$target.height();if(null!=c&&"top"==this.affixed)return c>e?"top":!1;if("bottom"==this.affixed)return null!=c?e+this.unpin<=f.top?!1:"bottom":a-d>=e+g?!1:"bottom";var h=null==this.affixed,i=h?e:f.top,j=h?g:b;return null!=c&&c>=e?"top":null!=d&&i+j>=a-d?"bottom":!1},c.prototype.getPinnedOffset=function(){if(this.pinnedOffset)return this.pinnedOffset;this.$element.removeClass(c.RESET).addClass("affix");var a=this.$target.scrollTop(),b=this.$element.offset();return this.pinnedOffset=b.top-a},c.prototype.checkPositionWithEventLoop=function(){setTimeout(a.proxy(this.checkPosition,this),1)},c.prototype.checkPosition=function(){if(this.$element.is(":visible")){var b=this.$element.height(),d=this.options.offset,e=d.top,f=d.bottom,g=Math.max(a(document).height(),a(document.body).height());"object"!=typeof d&&(f=e=d),"function"==typeof e&&(e=d.top(this.$element)),"function"==typeof f&&(f=d.bottom(this.$element));var h=this.getState(g,b,e,f);if(this.affixed!=h){null!=this.unpin&&this.$element.css("top","");var i="affix"+(h?"-"+h:""),j=a.Event(i+".bs.affix");if(this.$element.trigger(j),j.isDefaultPrevented())return;this.affixed=h,this.unpin="bottom"==h?this.getPinnedOffset():null,this.$element.removeClass(c.RESET).addClass(i).trigger(i.replace("affix","affixed")+".bs.affix")}"bottom"==h&&this.$element.offset({top:g-b-f})}};var d=a.fn.affix;a.fn.affix=b,a.fn.affix.Constructor=c,a.fn.affix.noConflict=function(){return a.fn.affix=d,this},a(window).on("load",function(){a('[data-spy="affix"]').each(function(){var c=a(this),d=c.data();d.offset=d.offset||{},null!=d.offsetBottom&&(d.offset.bottom=d.offsetBottom),null!=d.offsetTop&&(d.offset.top=d.offsetTop),b.call(c,d)})})}(jQuery);

/* - ++resource++orderedselect_input.js - */
function moveItems(from, to)
  {
  // shortcuts for selection fields
  var src = document.getElementById(from);
  var tgt = document.getElementById(to);

  if (src.selectedIndex == -1) selectionError();
  else
    {
    // iterate over all selected items
    // --> attribute "selectedIndex" doesn't support multiple selection.
    // Anyway, it works here, as a moved item isn't selected anymore,
    // thus "selectedIndex" indicating the "next" selected item :)
    while (src.selectedIndex > -1)
      if (src.options[src.selectedIndex].selected)
        {
        // create a new virtal object with values of item to copy
        temp = new Option(src.options[src.selectedIndex].text,
                      src.options[src.selectedIndex].value);
        // append virtual object to targe
        tgt.options[tgt.length] = temp;
        // want to select newly created item
        temp.selected = true;
        // delete moved item in source
        src.options[src.selectedIndex] = null;
      }
    }
  }

// move item from "from" selection to "to" selection
function from2to(name)
  {
  moveItems(name+"-from", name+"-to");
  copyDataForSubmit(name);
  }

// move item from "to" selection back to "from" selection
function to2from(name)
  {
  moveItems(name+"-to", name+"-from");
  copyDataForSubmit(name);
  }

function swapFields(a, b)
  {
  // swap text
  var temp = a.text;
  a.text = b.text;
  b.text = temp;
  // swap value
  temp = a.value;
  a.value = b.value;
  b.value = temp;
  // swap selection
  temp = a.selected;
  a.selected = b.selected;
  b.selected = temp;
  }

// move selected item in "to" selection one up
function moveUp(name)
  {
  // shortcuts for selection field
  var toSel = document.getElementById(name+"-to");

  if (toSel.selectedIndex == -1)
      selectionError();
  else for (var i = 1; i < toSel.length; i++)
    if (toSel.options[i].selected)
      {
      swapFields(toSel.options[i-1], toSel.options[i]);
      copyDataForSubmit(name);
      }
  }

// move selected item in "to" selection one down
function moveDown(name)
  {
    // shortcuts for selection field
    var toSel = document.getElementById(name+"-to");

    if (toSel.selectedIndex == -1) {
        selectionError();
    } else {
      for (var i = toSel.length-2; i >= 0; i--) {
        if (toSel.options[i].selected) {
          swapFields(toSel.options[i+1], toSel.options[i]);
        }
      }
      copyDataForSubmit(name);
    }
  }

// copy each item of "toSel" into one hidden input field
function copyDataForSubmit(name)
  {
  // shortcuts for selection field and hidden data field
  var toSel = document.getElementById(name+"-to");
  var toDataContainer = document.getElementById(name+"-toDataContainer");

  // delete all child nodes (--> complete content) of "toDataContainer" span
  while (toDataContainer.hasChildNodes())
      toDataContainer.removeChild(toDataContainer.firstChild);

  // create new hidden input fields - one for each selection item of
  // "to" selection
  for (var i = 0; i < toSel.options.length; i++)
    {
    // create virtual node with suitable attributes
    var newNode = document.createElement("input");
    newNode.setAttribute("name", name.replace(/-/g, '.')+':list');
    newNode.setAttribute("type", "hidden");
    newNode.setAttribute("value",toSel.options[i].value );

    // actually append virtual node to DOM tree
    toDataContainer.appendChild(newNode);
    }
  }

// error message for missing selection
function selectionError()
  {alert("Must select something!")}


/* - ++resource++plone.formwidget.geolocation/libs.js - */
/*
 Leaflet, a JavaScript library for mobile-friendly interactive maps. http://leafletjs.com
 (c) 2010-2013, Vladimir Agafonkin
 (c) 2010-2011, CloudMade
*/
(function (window, document, undefined) {
var oldL = window.L,
    L = {};

L.version = '0.7.7';

// define Leaflet as a global L variable, saving the original L to restore later if needed

L.noConflict = function () {
	window.L = oldL;
	return this;
};

window.L = L;


/*
 * L.Util contains various utility functions used throughout Leaflet code.
 */

L.Util = {
	extend: function (dest) { // (Object[, Object, ...]) ->
		var sources = Array.prototype.slice.call(arguments, 1),
		    i, j, len, src;

		for (j = 0, len = sources.length; j < len; j++) {
			src = sources[j] || {};
			for (i in src) {
				if (src.hasOwnProperty(i)) {
					dest[i] = src[i];
				}
			}
		}
		return dest;
	},

	bind: function (fn, obj) { // (Function, Object) -> Function
		var args = arguments.length > 2 ? Array.prototype.slice.call(arguments, 2) : null;
		return function () {
			return fn.apply(obj, args || arguments);
		};
	},

	stamp: (function () {
		var lastId = 0,
		    key = '_leaflet_id';
		return function (obj) {
			obj[key] = obj[key] || ++lastId;
			return obj[key];
		};
	}()),

	invokeEach: function (obj, method, context) {
		var i, args;

		if (typeof obj === 'object') {
			args = Array.prototype.slice.call(arguments, 3);

			for (i in obj) {
				method.apply(context, [i, obj[i]].concat(args));
			}
			return true;
		}

		return false;
	},

	limitExecByInterval: function (fn, time, context) {
		var lock, execOnUnlock;

		return function wrapperFn() {
			var args = arguments;

			if (lock) {
				execOnUnlock = true;
				return;
			}

			lock = true;

			setTimeout(function () {
				lock = false;

				if (execOnUnlock) {
					wrapperFn.apply(context, args);
					execOnUnlock = false;
				}
			}, time);

			fn.apply(context, args);
		};
	},

	falseFn: function () {
		return false;
	},

	formatNum: function (num, digits) {
		var pow = Math.pow(10, digits || 5);
		return Math.round(num * pow) / pow;
	},

	trim: function (str) {
		return str.trim ? str.trim() : str.replace(/^\s+|\s+$/g, '');
	},

	splitWords: function (str) {
		return L.Util.trim(str).split(/\s+/);
	},

	setOptions: function (obj, options) {
		obj.options = L.extend({}, obj.options, options);
		return obj.options;
	},

	getParamString: function (obj, existingUrl, uppercase) {
		var params = [];
		for (var i in obj) {
			params.push(encodeURIComponent(uppercase ? i.toUpperCase() : i) + '=' + encodeURIComponent(obj[i]));
		}
		return ((!existingUrl || existingUrl.indexOf('?') === -1) ? '?' : '&') + params.join('&');
	},
	template: function (str, data) {
		return str.replace(/\{ *([\w_]+) *\}/g, function (str, key) {
			var value = data[key];
			if (value === undefined) {
				throw new Error('No value provided for variable ' + str);
			} else if (typeof value === 'function') {
				value = value(data);
			}
			return value;
		});
	},

	isArray: Array.isArray || function (obj) {
		return (Object.prototype.toString.call(obj) === '[object Array]');
	},

	emptyImageUrl: 'data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs='
};

(function () {

	// inspired by http://paulirish.com/2011/requestanimationframe-for-smart-animating/

	function getPrefixed(name) {
		var i, fn,
		    prefixes = ['webkit', 'moz', 'o', 'ms'];

		for (i = 0; i < prefixes.length && !fn; i++) {
			fn = window[prefixes[i] + name];
		}

		return fn;
	}

	var lastTime = 0;

	function timeoutDefer(fn) {
		var time = +new Date(),
		    timeToCall = Math.max(0, 16 - (time - lastTime));

		lastTime = time + timeToCall;
		return window.setTimeout(fn, timeToCall);
	}

	var requestFn = window.requestAnimationFrame ||
	        getPrefixed('RequestAnimationFrame') || timeoutDefer;

	var cancelFn = window.cancelAnimationFrame ||
	        getPrefixed('CancelAnimationFrame') ||
	        getPrefixed('CancelRequestAnimationFrame') ||
	        function (id) { window.clearTimeout(id); };


	L.Util.requestAnimFrame = function (fn, context, immediate, element) {
		fn = L.bind(fn, context);

		if (immediate && requestFn === timeoutDefer) {
			fn();
		} else {
			return requestFn.call(window, fn, element);
		}
	};

	L.Util.cancelAnimFrame = function (id) {
		if (id) {
			cancelFn.call(window, id);
		}
	};

}());

// shortcuts for most used utility functions
L.extend = L.Util.extend;
L.bind = L.Util.bind;
L.stamp = L.Util.stamp;
L.setOptions = L.Util.setOptions;


/*
 * L.Class powers the OOP facilities of the library.
 * Thanks to John Resig and Dean Edwards for inspiration!
 */

L.Class = function () {};

L.Class.extend = function (props) {

	// extended class with the new prototype
	var NewClass = function () {

		// call the constructor
		if (this.initialize) {
			this.initialize.apply(this, arguments);
		}

		// call all constructor hooks
		if (this._initHooks) {
			this.callInitHooks();
		}
	};

	// instantiate class without calling constructor
	var F = function () {};
	F.prototype = this.prototype;

	var proto = new F();
	proto.constructor = NewClass;

	NewClass.prototype = proto;

	//inherit parent's statics
	for (var i in this) {
		if (this.hasOwnProperty(i) && i !== 'prototype') {
			NewClass[i] = this[i];
		}
	}

	// mix static properties into the class
	if (props.statics) {
		L.extend(NewClass, props.statics);
		delete props.statics;
	}

	// mix includes into the prototype
	if (props.includes) {
		L.Util.extend.apply(null, [proto].concat(props.includes));
		delete props.includes;
	}

	// merge options
	if (props.options && proto.options) {
		props.options = L.extend({}, proto.options, props.options);
	}

	// mix given properties into the prototype
	L.extend(proto, props);

	proto._initHooks = [];

	var parent = this;
	// jshint camelcase: false
	NewClass.__super__ = parent.prototype;

	// add method for calling all hooks
	proto.callInitHooks = function () {

		if (this._initHooksCalled) { return; }

		if (parent.prototype.callInitHooks) {
			parent.prototype.callInitHooks.call(this);
		}

		this._initHooksCalled = true;

		for (var i = 0, len = proto._initHooks.length; i < len; i++) {
			proto._initHooks[i].call(this);
		}
	};

	return NewClass;
};


// method for adding properties to prototype
L.Class.include = function (props) {
	L.extend(this.prototype, props);
};

// merge new default options to the Class
L.Class.mergeOptions = function (options) {
	L.extend(this.prototype.options, options);
};

// add a constructor hook
L.Class.addInitHook = function (fn) { // (Function) || (String, args...)
	var args = Array.prototype.slice.call(arguments, 1);

	var init = typeof fn === 'function' ? fn : function () {
		this[fn].apply(this, args);
	};

	this.prototype._initHooks = this.prototype._initHooks || [];
	this.prototype._initHooks.push(init);
};


/*
 * L.Mixin.Events is used to add custom events functionality to Leaflet classes.
 */

var eventsKey = '_leaflet_events';

L.Mixin = {};

L.Mixin.Events = {

	addEventListener: function (types, fn, context) { // (String, Function[, Object]) or (Object[, Object])

		// types can be a map of types/handlers
		if (L.Util.invokeEach(types, this.addEventListener, this, fn, context)) { return this; }

		var events = this[eventsKey] = this[eventsKey] || {},
		    contextId = context && context !== this && L.stamp(context),
		    i, len, event, type, indexKey, indexLenKey, typeIndex;

		// types can be a string of space-separated words
		types = L.Util.splitWords(types);

		for (i = 0, len = types.length; i < len; i++) {
			event = {
				action: fn,
				context: context || this
			};
			type = types[i];

			if (contextId) {
				// store listeners of a particular context in a separate hash (if it has an id)
				// gives a major performance boost when removing thousands of map layers

				indexKey = type + '_idx';
				indexLenKey = indexKey + '_len';

				typeIndex = events[indexKey] = events[indexKey] || {};

				if (!typeIndex[contextId]) {
					typeIndex[contextId] = [];

					// keep track of the number of keys in the index to quickly check if it's empty
					events[indexLenKey] = (events[indexLenKey] || 0) + 1;
				}

				typeIndex[contextId].push(event);


			} else {
				events[type] = events[type] || [];
				events[type].push(event);
			}
		}

		return this;
	},

	hasEventListeners: function (type) { // (String) -> Boolean
		var events = this[eventsKey];
		return !!events && ((type in events && events[type].length > 0) ||
		                    (type + '_idx' in events && events[type + '_idx_len'] > 0));
	},

	removeEventListener: function (types, fn, context) { // ([String, Function, Object]) or (Object[, Object])

		if (!this[eventsKey]) {
			return this;
		}

		if (!types) {
			return this.clearAllEventListeners();
		}

		if (L.Util.invokeEach(types, this.removeEventListener, this, fn, context)) { return this; }

		var events = this[eventsKey],
		    contextId = context && context !== this && L.stamp(context),
		    i, len, type, listeners, j, indexKey, indexLenKey, typeIndex, removed;

		types = L.Util.splitWords(types);

		for (i = 0, len = types.length; i < len; i++) {
			type = types[i];
			indexKey = type + '_idx';
			indexLenKey = indexKey + '_len';

			typeIndex = events[indexKey];

			if (!fn) {
				// clear all listeners for a type if function isn't specified
				delete events[type];
				delete events[indexKey];
				delete events[indexLenKey];

			} else {
				listeners = contextId && typeIndex ? typeIndex[contextId] : events[type];

				if (listeners) {
					for (j = listeners.length - 1; j >= 0; j--) {
						if ((listeners[j].action === fn) && (!context || (listeners[j].context === context))) {
							removed = listeners.splice(j, 1);
							// set the old action to a no-op, because it is possible
							// that the listener is being iterated over as part of a dispatch
							removed[0].action = L.Util.falseFn;
						}
					}

					if (context && typeIndex && (listeners.length === 0)) {
						delete typeIndex[contextId];
						events[indexLenKey]--;
					}
				}
			}
		}

		return this;
	},

	clearAllEventListeners: function () {
		delete this[eventsKey];
		return this;
	},

	fireEvent: function (type, data) { // (String[, Object])
		if (!this.hasEventListeners(type)) {
			return this;
		}

		var event = L.Util.extend({}, data, { type: type, target: this });

		var events = this[eventsKey],
		    listeners, i, len, typeIndex, contextId;

		if (events[type]) {
			// make sure adding/removing listeners inside other listeners won't cause infinite loop
			listeners = events[type].slice();

			for (i = 0, len = listeners.length; i < len; i++) {
				listeners[i].action.call(listeners[i].context, event);
			}
		}

		// fire event for the context-indexed listeners as well
		typeIndex = events[type + '_idx'];

		for (contextId in typeIndex) {
			listeners = typeIndex[contextId].slice();

			if (listeners) {
				for (i = 0, len = listeners.length; i < len; i++) {
					listeners[i].action.call(listeners[i].context, event);
				}
			}
		}

		return this;
	},

	addOneTimeEventListener: function (types, fn, context) {

		if (L.Util.invokeEach(types, this.addOneTimeEventListener, this, fn, context)) { return this; }

		var handler = L.bind(function () {
			this
			    .removeEventListener(types, fn, context)
			    .removeEventListener(types, handler, context);
		}, this);

		return this
		    .addEventListener(types, fn, context)
		    .addEventListener(types, handler, context);
	}
};

L.Mixin.Events.on = L.Mixin.Events.addEventListener;
L.Mixin.Events.off = L.Mixin.Events.removeEventListener;
L.Mixin.Events.once = L.Mixin.Events.addOneTimeEventListener;
L.Mixin.Events.fire = L.Mixin.Events.fireEvent;


/*
 * L.Browser handles different browser and feature detections for internal Leaflet use.
 */

(function () {

	var ie = 'ActiveXObject' in window,
		ielt9 = ie && !document.addEventListener,

	    // terrible browser detection to work around Safari / iOS / Android browser bugs
	    ua = navigator.userAgent.toLowerCase(),
	    webkit = ua.indexOf('webkit') !== -1,
	    chrome = ua.indexOf('chrome') !== -1,
	    phantomjs = ua.indexOf('phantom') !== -1,
	    android = ua.indexOf('android') !== -1,
	    android23 = ua.search('android [23]') !== -1,
		gecko = ua.indexOf('gecko') !== -1,

	    mobile = typeof orientation !== undefined + '',
	    msPointer = !window.PointerEvent && window.MSPointerEvent,
		pointer = (window.PointerEvent && window.navigator.pointerEnabled) ||
				  msPointer,
	    retina = ('devicePixelRatio' in window && window.devicePixelRatio > 1) ||
	             ('matchMedia' in window && window.matchMedia('(min-resolution:144dpi)') &&
	              window.matchMedia('(min-resolution:144dpi)').matches),

	    doc = document.documentElement,
	    ie3d = ie && ('transition' in doc.style),
	    webkit3d = ('WebKitCSSMatrix' in window) && ('m11' in new window.WebKitCSSMatrix()) && !android23,
	    gecko3d = 'MozPerspective' in doc.style,
	    opera3d = 'OTransition' in doc.style,
	    any3d = !window.L_DISABLE_3D && (ie3d || webkit3d || gecko3d || opera3d) && !phantomjs;

	var touch = !window.L_NO_TOUCH && !phantomjs && (pointer || 'ontouchstart' in window ||
		(window.DocumentTouch && document instanceof window.DocumentTouch));

	L.Browser = {
		ie: ie,
		ielt9: ielt9,
		webkit: webkit,
		gecko: gecko && !webkit && !window.opera && !ie,

		android: android,
		android23: android23,

		chrome: chrome,

		ie3d: ie3d,
		webkit3d: webkit3d,
		gecko3d: gecko3d,
		opera3d: opera3d,
		any3d: any3d,

		mobile: mobile,
		mobileWebkit: mobile && webkit,
		mobileWebkit3d: mobile && webkit3d,
		mobileOpera: mobile && window.opera,

		touch: touch,
		msPointer: msPointer,
		pointer: pointer,

		retina: retina
	};

}());


/*
 * L.Point represents a point with x and y coordinates.
 */

L.Point = function (/*Number*/ x, /*Number*/ y, /*Boolean*/ round) {
	this.x = (round ? Math.round(x) : x);
	this.y = (round ? Math.round(y) : y);
};

L.Point.prototype = {

	clone: function () {
		return new L.Point(this.x, this.y);
	},

	// non-destructive, returns a new point
	add: function (point) {
		return this.clone()._add(L.point(point));
	},

	// destructive, used directly for performance in situations where it's safe to modify existing point
	_add: function (point) {
		this.x += point.x;
		this.y += point.y;
		return this;
	},

	subtract: function (point) {
		return this.clone()._subtract(L.point(point));
	},

	_subtract: function (point) {
		this.x -= point.x;
		this.y -= point.y;
		return this;
	},

	divideBy: function (num) {
		return this.clone()._divideBy(num);
	},

	_divideBy: function (num) {
		this.x /= num;
		this.y /= num;
		return this;
	},

	multiplyBy: function (num) {
		return this.clone()._multiplyBy(num);
	},

	_multiplyBy: function (num) {
		this.x *= num;
		this.y *= num;
		return this;
	},

	round: function () {
		return this.clone()._round();
	},

	_round: function () {
		this.x = Math.round(this.x);
		this.y = Math.round(this.y);
		return this;
	},

	floor: function () {
		return this.clone()._floor();
	},

	_floor: function () {
		this.x = Math.floor(this.x);
		this.y = Math.floor(this.y);
		return this;
	},

	distanceTo: function (point) {
		point = L.point(point);

		var x = point.x - this.x,
		    y = point.y - this.y;

		return Math.sqrt(x * x + y * y);
	},

	equals: function (point) {
		point = L.point(point);

		return point.x === this.x &&
		       point.y === this.y;
	},

	contains: function (point) {
		point = L.point(point);

		return Math.abs(point.x) <= Math.abs(this.x) &&
		       Math.abs(point.y) <= Math.abs(this.y);
	},

	toString: function () {
		return 'Point(' +
		        L.Util.formatNum(this.x) + ', ' +
		        L.Util.formatNum(this.y) + ')';
	}
};

L.point = function (x, y, round) {
	if (x instanceof L.Point) {
		return x;
	}
	if (L.Util.isArray(x)) {
		return new L.Point(x[0], x[1]);
	}
	if (x === undefined || x === null) {
		return x;
	}
	return new L.Point(x, y, round);
};


/*
 * L.Bounds represents a rectangular area on the screen in pixel coordinates.
 */

L.Bounds = function (a, b) { //(Point, Point) or Point[]
	if (!a) { return; }

	var points = b ? [a, b] : a;

	for (var i = 0, len = points.length; i < len; i++) {
		this.extend(points[i]);
	}
};

L.Bounds.prototype = {
	// extend the bounds to contain the given point
	extend: function (point) { // (Point)
		point = L.point(point);

		if (!this.min && !this.max) {
			this.min = point.clone();
			this.max = point.clone();
		} else {
			this.min.x = Math.min(point.x, this.min.x);
			this.max.x = Math.max(point.x, this.max.x);
			this.min.y = Math.min(point.y, this.min.y);
			this.max.y = Math.max(point.y, this.max.y);
		}
		return this;
	},

	getCenter: function (round) { // (Boolean) -> Point
		return new L.Point(
		        (this.min.x + this.max.x) / 2,
		        (this.min.y + this.max.y) / 2, round);
	},

	getBottomLeft: function () { // -> Point
		return new L.Point(this.min.x, this.max.y);
	},

	getTopRight: function () { // -> Point
		return new L.Point(this.max.x, this.min.y);
	},

	getSize: function () {
		return this.max.subtract(this.min);
	},

	contains: function (obj) { // (Bounds) or (Point) -> Boolean
		var min, max;

		if (typeof obj[0] === 'number' || obj instanceof L.Point) {
			obj = L.point(obj);
		} else {
			obj = L.bounds(obj);
		}

		if (obj instanceof L.Bounds) {
			min = obj.min;
			max = obj.max;
		} else {
			min = max = obj;
		}

		return (min.x >= this.min.x) &&
		       (max.x <= this.max.x) &&
		       (min.y >= this.min.y) &&
		       (max.y <= this.max.y);
	},

	intersects: function (bounds) { // (Bounds) -> Boolean
		bounds = L.bounds(bounds);

		var min = this.min,
		    max = this.max,
		    min2 = bounds.min,
		    max2 = bounds.max,
		    xIntersects = (max2.x >= min.x) && (min2.x <= max.x),
		    yIntersects = (max2.y >= min.y) && (min2.y <= max.y);

		return xIntersects && yIntersects;
	},

	isValid: function () {
		return !!(this.min && this.max);
	}
};

L.bounds = function (a, b) { // (Bounds) or (Point, Point) or (Point[])
	if (!a || a instanceof L.Bounds) {
		return a;
	}
	return new L.Bounds(a, b);
};


/*
 * L.Transformation is an utility class to perform simple point transformations through a 2d-matrix.
 */

L.Transformation = function (a, b, c, d) {
	this._a = a;
	this._b = b;
	this._c = c;
	this._d = d;
};

L.Transformation.prototype = {
	transform: function (point, scale) { // (Point, Number) -> Point
		return this._transform(point.clone(), scale);
	},

	// destructive transform (faster)
	_transform: function (point, scale) {
		scale = scale || 1;
		point.x = scale * (this._a * point.x + this._b);
		point.y = scale * (this._c * point.y + this._d);
		return point;
	},

	untransform: function (point, scale) {
		scale = scale || 1;
		return new L.Point(
		        (point.x / scale - this._b) / this._a,
		        (point.y / scale - this._d) / this._c);
	}
};


/*
 * L.DomUtil contains various utility functions for working with DOM.
 */

L.DomUtil = {
	get: function (id) {
		return (typeof id === 'string' ? document.getElementById(id) : id);
	},

	getStyle: function (el, style) {

		var value = el.style[style];

		if (!value && el.currentStyle) {
			value = el.currentStyle[style];
		}

		if ((!value || value === 'auto') && document.defaultView) {
			var css = document.defaultView.getComputedStyle(el, null);
			value = css ? css[style] : null;
		}

		return value === 'auto' ? null : value;
	},

	getViewportOffset: function (element) {

		var top = 0,
		    left = 0,
		    el = element,
		    docBody = document.body,
		    docEl = document.documentElement,
		    pos;

		do {
			top  += el.offsetTop  || 0;
			left += el.offsetLeft || 0;

			//add borders
			top += parseInt(L.DomUtil.getStyle(el, 'borderTopWidth'), 10) || 0;
			left += parseInt(L.DomUtil.getStyle(el, 'borderLeftWidth'), 10) || 0;

			pos = L.DomUtil.getStyle(el, 'position');

			if (el.offsetParent === docBody && pos === 'absolute') { break; }

			if (pos === 'fixed') {
				top  += docBody.scrollTop  || docEl.scrollTop  || 0;
				left += docBody.scrollLeft || docEl.scrollLeft || 0;
				break;
			}

			if (pos === 'relative' && !el.offsetLeft) {
				var width = L.DomUtil.getStyle(el, 'width'),
				    maxWidth = L.DomUtil.getStyle(el, 'max-width'),
				    r = el.getBoundingClientRect();

				if (width !== 'none' || maxWidth !== 'none') {
					left += r.left + el.clientLeft;
				}

				//calculate full y offset since we're breaking out of the loop
				top += r.top + (docBody.scrollTop  || docEl.scrollTop  || 0);

				break;
			}

			el = el.offsetParent;

		} while (el);

		el = element;

		do {
			if (el === docBody) { break; }

			top  -= el.scrollTop  || 0;
			left -= el.scrollLeft || 0;

			el = el.parentNode;
		} while (el);

		return new L.Point(left, top);
	},

	documentIsLtr: function () {
		if (!L.DomUtil._docIsLtrCached) {
			L.DomUtil._docIsLtrCached = true;
			L.DomUtil._docIsLtr = L.DomUtil.getStyle(document.body, 'direction') === 'ltr';
		}
		return L.DomUtil._docIsLtr;
	},

	create: function (tagName, className, container) {

		var el = document.createElement(tagName);
		el.className = className;

		if (container) {
			container.appendChild(el);
		}

		return el;
	},

	hasClass: function (el, name) {
		if (el.classList !== undefined) {
			return el.classList.contains(name);
		}
		var className = L.DomUtil._getClass(el);
		return className.length > 0 && new RegExp('(^|\\s)' + name + '(\\s|$)').test(className);
	},

	addClass: function (el, name) {
		if (el.classList !== undefined) {
			var classes = L.Util.splitWords(name);
			for (var i = 0, len = classes.length; i < len; i++) {
				el.classList.add(classes[i]);
			}
		} else if (!L.DomUtil.hasClass(el, name)) {
			var className = L.DomUtil._getClass(el);
			L.DomUtil._setClass(el, (className ? className + ' ' : '') + name);
		}
	},

	removeClass: function (el, name) {
		if (el.classList !== undefined) {
			el.classList.remove(name);
		} else {
			L.DomUtil._setClass(el, L.Util.trim((' ' + L.DomUtil._getClass(el) + ' ').replace(' ' + name + ' ', ' ')));
		}
	},

	_setClass: function (el, name) {
		if (el.className.baseVal === undefined) {
			el.className = name;
		} else {
			// in case of SVG element
			el.className.baseVal = name;
		}
	},

	_getClass: function (el) {
		return el.className.baseVal === undefined ? el.className : el.className.baseVal;
	},

	setOpacity: function (el, value) {

		if ('opacity' in el.style) {
			el.style.opacity = value;

		} else if ('filter' in el.style) {

			var filter = false,
			    filterName = 'DXImageTransform.Microsoft.Alpha';

			// filters collection throws an error if we try to retrieve a filter that doesn't exist
			try {
				filter = el.filters.item(filterName);
			} catch (e) {
				// don't set opacity to 1 if we haven't already set an opacity,
				// it isn't needed and breaks transparent pngs.
				if (value === 1) { return; }
			}

			value = Math.round(value * 100);

			if (filter) {
				filter.Enabled = (value !== 100);
				filter.Opacity = value;
			} else {
				el.style.filter += ' progid:' + filterName + '(opacity=' + value + ')';
			}
		}
	},

	testProp: function (props) {

		var style = document.documentElement.style;

		for (var i = 0; i < props.length; i++) {
			if (props[i] in style) {
				return props[i];
			}
		}
		return false;
	},

	getTranslateString: function (point) {
		// on WebKit browsers (Chrome/Safari/iOS Safari/Android) using translate3d instead of translate
		// makes animation smoother as it ensures HW accel is used. Firefox 13 doesn't care
		// (same speed either way), Opera 12 doesn't support translate3d

		var is3d = L.Browser.webkit3d,
		    open = 'translate' + (is3d ? '3d' : '') + '(',
		    close = (is3d ? ',0' : '') + ')';

		return open + point.x + 'px,' + point.y + 'px' + close;
	},

	getScaleString: function (scale, origin) {

		var preTranslateStr = L.DomUtil.getTranslateString(origin.add(origin.multiplyBy(-1 * scale))),
		    scaleStr = ' scale(' + scale + ') ';

		return preTranslateStr + scaleStr;
	},

	setPosition: function (el, point, disable3D) { // (HTMLElement, Point[, Boolean])

		// jshint camelcase: false
		el._leaflet_pos = point;

		if (!disable3D && L.Browser.any3d) {
			el.style[L.DomUtil.TRANSFORM] =  L.DomUtil.getTranslateString(point);
		} else {
			el.style.left = point.x + 'px';
			el.style.top = point.y + 'px';
		}
	},

	getPosition: function (el) {
		// this method is only used for elements previously positioned using setPosition,
		// so it's safe to cache the position for performance

		// jshint camelcase: false
		return el._leaflet_pos;
	}
};


// prefix style property names

L.DomUtil.TRANSFORM = L.DomUtil.testProp(
        ['transform', 'WebkitTransform', 'OTransform', 'MozTransform', 'msTransform']);

// webkitTransition comes first because some browser versions that drop vendor prefix don't do
// the same for the transitionend event, in particular the Android 4.1 stock browser

L.DomUtil.TRANSITION = L.DomUtil.testProp(
        ['webkitTransition', 'transition', 'OTransition', 'MozTransition', 'msTransition']);

L.DomUtil.TRANSITION_END =
        L.DomUtil.TRANSITION === 'webkitTransition' || L.DomUtil.TRANSITION === 'OTransition' ?
        L.DomUtil.TRANSITION + 'End' : 'transitionend';

(function () {
    if ('onselectstart' in document) {
        L.extend(L.DomUtil, {
            disableTextSelection: function () {
                L.DomEvent.on(window, 'selectstart', L.DomEvent.preventDefault);
            },

            enableTextSelection: function () {
                L.DomEvent.off(window, 'selectstart', L.DomEvent.preventDefault);
            }
        });
    } else {
        var userSelectProperty = L.DomUtil.testProp(
            ['userSelect', 'WebkitUserSelect', 'OUserSelect', 'MozUserSelect', 'msUserSelect']);

        L.extend(L.DomUtil, {
            disableTextSelection: function () {
                if (userSelectProperty) {
                    var style = document.documentElement.style;
                    this._userSelect = style[userSelectProperty];
                    style[userSelectProperty] = 'none';
                }
            },

            enableTextSelection: function () {
                if (userSelectProperty) {
                    document.documentElement.style[userSelectProperty] = this._userSelect;
                    delete this._userSelect;
                }
            }
        });
    }

	L.extend(L.DomUtil, {
		disableImageDrag: function () {
			L.DomEvent.on(window, 'dragstart', L.DomEvent.preventDefault);
		},

		enableImageDrag: function () {
			L.DomEvent.off(window, 'dragstart', L.DomEvent.preventDefault);
		}
	});
})();


/*
 * L.LatLng represents a geographical point with latitude and longitude coordinates.
 */

L.LatLng = function (lat, lng, alt) { // (Number, Number, Number)
	lat = parseFloat(lat);
	lng = parseFloat(lng);

	if (isNaN(lat) || isNaN(lng)) {
		throw new Error('Invalid LatLng object: (' + lat + ', ' + lng + ')');
	}

	this.lat = lat;
	this.lng = lng;

	if (alt !== undefined) {
		this.alt = parseFloat(alt);
	}
};

L.extend(L.LatLng, {
	DEG_TO_RAD: Math.PI / 180,
	RAD_TO_DEG: 180 / Math.PI,
	MAX_MARGIN: 1.0E-9 // max margin of error for the "equals" check
});

L.LatLng.prototype = {
	equals: function (obj) { // (LatLng) -> Boolean
		if (!obj) { return false; }

		obj = L.latLng(obj);

		var margin = Math.max(
		        Math.abs(this.lat - obj.lat),
		        Math.abs(this.lng - obj.lng));

		return margin <= L.LatLng.MAX_MARGIN;
	},

	toString: function (precision) { // (Number) -> String
		return 'LatLng(' +
		        L.Util.formatNum(this.lat, precision) + ', ' +
		        L.Util.formatNum(this.lng, precision) + ')';
	},

	// Haversine distance formula, see http://en.wikipedia.org/wiki/Haversine_formula
	// TODO move to projection code, LatLng shouldn't know about Earth
	distanceTo: function (other) { // (LatLng) -> Number
		other = L.latLng(other);

		var R = 6378137, // earth radius in meters
		    d2r = L.LatLng.DEG_TO_RAD,
		    dLat = (other.lat - this.lat) * d2r,
		    dLon = (other.lng - this.lng) * d2r,
		    lat1 = this.lat * d2r,
		    lat2 = other.lat * d2r,
		    sin1 = Math.sin(dLat / 2),
		    sin2 = Math.sin(dLon / 2);

		var a = sin1 * sin1 + sin2 * sin2 * Math.cos(lat1) * Math.cos(lat2);

		return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
	},

	wrap: function (a, b) { // (Number, Number) -> LatLng
		var lng = this.lng;

		a = a || -180;
		b = b ||  180;

		lng = (lng + b) % (b - a) + (lng < a || lng === b ? b : a);

		return new L.LatLng(this.lat, lng);
	}
};

L.latLng = function (a, b) { // (LatLng) or ([Number, Number]) or (Number, Number)
	if (a instanceof L.LatLng) {
		return a;
	}
	if (L.Util.isArray(a)) {
		if (typeof a[0] === 'number' || typeof a[0] === 'string') {
			return new L.LatLng(a[0], a[1], a[2]);
		} else {
			return null;
		}
	}
	if (a === undefined || a === null) {
		return a;
	}
	if (typeof a === 'object' && 'lat' in a) {
		return new L.LatLng(a.lat, 'lng' in a ? a.lng : a.lon);
	}
	if (b === undefined) {
		return null;
	}
	return new L.LatLng(a, b);
};



/*
 * L.LatLngBounds represents a rectangular area on the map in geographical coordinates.
 */

L.LatLngBounds = function (southWest, northEast) { // (LatLng, LatLng) or (LatLng[])
	if (!southWest) { return; }

	var latlngs = northEast ? [southWest, northEast] : southWest;

	for (var i = 0, len = latlngs.length; i < len; i++) {
		this.extend(latlngs[i]);
	}
};

L.LatLngBounds.prototype = {
	// extend the bounds to contain the given point or bounds
	extend: function (obj) { // (LatLng) or (LatLngBounds)
		if (!obj) { return this; }

		var latLng = L.latLng(obj);
		if (latLng !== null) {
			obj = latLng;
		} else {
			obj = L.latLngBounds(obj);
		}

		if (obj instanceof L.LatLng) {
			if (!this._southWest && !this._northEast) {
				this._southWest = new L.LatLng(obj.lat, obj.lng);
				this._northEast = new L.LatLng(obj.lat, obj.lng);
			} else {
				this._southWest.lat = Math.min(obj.lat, this._southWest.lat);
				this._southWest.lng = Math.min(obj.lng, this._southWest.lng);

				this._northEast.lat = Math.max(obj.lat, this._northEast.lat);
				this._northEast.lng = Math.max(obj.lng, this._northEast.lng);
			}
		} else if (obj instanceof L.LatLngBounds) {
			this.extend(obj._southWest);
			this.extend(obj._northEast);
		}
		return this;
	},

	// extend the bounds by a percentage
	pad: function (bufferRatio) { // (Number) -> LatLngBounds
		var sw = this._southWest,
		    ne = this._northEast,
		    heightBuffer = Math.abs(sw.lat - ne.lat) * bufferRatio,
		    widthBuffer = Math.abs(sw.lng - ne.lng) * bufferRatio;

		return new L.LatLngBounds(
		        new L.LatLng(sw.lat - heightBuffer, sw.lng - widthBuffer),
		        new L.LatLng(ne.lat + heightBuffer, ne.lng + widthBuffer));
	},

	getCenter: function () { // -> LatLng
		return new L.LatLng(
		        (this._southWest.lat + this._northEast.lat) / 2,
		        (this._southWest.lng + this._northEast.lng) / 2);
	},

	getSouthWest: function () {
		return this._southWest;
	},

	getNorthEast: function () {
		return this._northEast;
	},

	getNorthWest: function () {
		return new L.LatLng(this.getNorth(), this.getWest());
	},

	getSouthEast: function () {
		return new L.LatLng(this.getSouth(), this.getEast());
	},

	getWest: function () {
		return this._southWest.lng;
	},

	getSouth: function () {
		return this._southWest.lat;
	},

	getEast: function () {
		return this._northEast.lng;
	},

	getNorth: function () {
		return this._northEast.lat;
	},

	contains: function (obj) { // (LatLngBounds) or (LatLng) -> Boolean
		if (typeof obj[0] === 'number' || obj instanceof L.LatLng) {
			obj = L.latLng(obj);
		} else {
			obj = L.latLngBounds(obj);
		}

		var sw = this._southWest,
		    ne = this._northEast,
		    sw2, ne2;

		if (obj instanceof L.LatLngBounds) {
			sw2 = obj.getSouthWest();
			ne2 = obj.getNorthEast();
		} else {
			sw2 = ne2 = obj;
		}

		return (sw2.lat >= sw.lat) && (ne2.lat <= ne.lat) &&
		       (sw2.lng >= sw.lng) && (ne2.lng <= ne.lng);
	},

	intersects: function (bounds) { // (LatLngBounds)
		bounds = L.latLngBounds(bounds);

		var sw = this._southWest,
		    ne = this._northEast,
		    sw2 = bounds.getSouthWest(),
		    ne2 = bounds.getNorthEast(),

		    latIntersects = (ne2.lat >= sw.lat) && (sw2.lat <= ne.lat),
		    lngIntersects = (ne2.lng >= sw.lng) && (sw2.lng <= ne.lng);

		return latIntersects && lngIntersects;
	},

	toBBoxString: function () {
		return [this.getWest(), this.getSouth(), this.getEast(), this.getNorth()].join(',');
	},

	equals: function (bounds) { // (LatLngBounds)
		if (!bounds) { return false; }

		bounds = L.latLngBounds(bounds);

		return this._southWest.equals(bounds.getSouthWest()) &&
		       this._northEast.equals(bounds.getNorthEast());
	},

	isValid: function () {
		return !!(this._southWest && this._northEast);
	}
};

//TODO International date line?

L.latLngBounds = function (a, b) { // (LatLngBounds) or (LatLng, LatLng)
	if (!a || a instanceof L.LatLngBounds) {
		return a;
	}
	return new L.LatLngBounds(a, b);
};


/*
 * L.Projection contains various geographical projections used by CRS classes.
 */

L.Projection = {};


/*
 * Spherical Mercator is the most popular map projection, used by EPSG:3857 CRS used by default.
 */

L.Projection.SphericalMercator = {
	MAX_LATITUDE: 85.0511287798,

	project: function (latlng) { // (LatLng) -> Point
		var d = L.LatLng.DEG_TO_RAD,
		    max = this.MAX_LATITUDE,
		    lat = Math.max(Math.min(max, latlng.lat), -max),
		    x = latlng.lng * d,
		    y = lat * d;

		y = Math.log(Math.tan((Math.PI / 4) + (y / 2)));

		return new L.Point(x, y);
	},

	unproject: function (point) { // (Point, Boolean) -> LatLng
		var d = L.LatLng.RAD_TO_DEG,
		    lng = point.x * d,
		    lat = (2 * Math.atan(Math.exp(point.y)) - (Math.PI / 2)) * d;

		return new L.LatLng(lat, lng);
	}
};


/*
 * Simple equirectangular (Plate Carree) projection, used by CRS like EPSG:4326 and Simple.
 */

L.Projection.LonLat = {
	project: function (latlng) {
		return new L.Point(latlng.lng, latlng.lat);
	},

	unproject: function (point) {
		return new L.LatLng(point.y, point.x);
	}
};


/*
 * L.CRS is a base object for all defined CRS (Coordinate Reference Systems) in Leaflet.
 */

L.CRS = {
	latLngToPoint: function (latlng, zoom) { // (LatLng, Number) -> Point
		var projectedPoint = this.projection.project(latlng),
		    scale = this.scale(zoom);

		return this.transformation._transform(projectedPoint, scale);
	},

	pointToLatLng: function (point, zoom) { // (Point, Number[, Boolean]) -> LatLng
		var scale = this.scale(zoom),
		    untransformedPoint = this.transformation.untransform(point, scale);

		return this.projection.unproject(untransformedPoint);
	},

	project: function (latlng) {
		return this.projection.project(latlng);
	},

	scale: function (zoom) {
		return 256 * Math.pow(2, zoom);
	},

	getSize: function (zoom) {
		var s = this.scale(zoom);
		return L.point(s, s);
	}
};


/*
 * A simple CRS that can be used for flat non-Earth maps like panoramas or game maps.
 */

L.CRS.Simple = L.extend({}, L.CRS, {
	projection: L.Projection.LonLat,
	transformation: new L.Transformation(1, 0, -1, 0),

	scale: function (zoom) {
		return Math.pow(2, zoom);
	}
});


/*
 * L.CRS.EPSG3857 (Spherical Mercator) is the most common CRS for web mapping
 * and is used by Leaflet by default.
 */

L.CRS.EPSG3857 = L.extend({}, L.CRS, {
	code: 'EPSG:3857',

	projection: L.Projection.SphericalMercator,
	transformation: new L.Transformation(0.5 / Math.PI, 0.5, -0.5 / Math.PI, 0.5),

	project: function (latlng) { // (LatLng) -> Point
		var projectedPoint = this.projection.project(latlng),
		    earthRadius = 6378137;
		return projectedPoint.multiplyBy(earthRadius);
	}
});

L.CRS.EPSG900913 = L.extend({}, L.CRS.EPSG3857, {
	code: 'EPSG:900913'
});


/*
 * L.CRS.EPSG4326 is a CRS popular among advanced GIS specialists.
 */

L.CRS.EPSG4326 = L.extend({}, L.CRS, {
	code: 'EPSG:4326',

	projection: L.Projection.LonLat,
	transformation: new L.Transformation(1 / 360, 0.5, -1 / 360, 0.5)
});


/*
 * L.Map is the central class of the API - it is used to create a map.
 */

L.Map = L.Class.extend({

	includes: L.Mixin.Events,

	options: {
		crs: L.CRS.EPSG3857,

		/*
		center: LatLng,
		zoom: Number,
		layers: Array,
		*/

		fadeAnimation: L.DomUtil.TRANSITION && !L.Browser.android23,
		trackResize: true,
		markerZoomAnimation: L.DomUtil.TRANSITION && L.Browser.any3d
	},

	initialize: function (id, options) { // (HTMLElement or String, Object)
		options = L.setOptions(this, options);


		this._initContainer(id);
		this._initLayout();

		// hack for https://github.com/Leaflet/Leaflet/issues/1980
		this._onResize = L.bind(this._onResize, this);

		this._initEvents();

		if (options.maxBounds) {
			this.setMaxBounds(options.maxBounds);
		}

		if (options.center && options.zoom !== undefined) {
			this.setView(L.latLng(options.center), options.zoom, {reset: true});
		}

		this._handlers = [];

		this._layers = {};
		this._zoomBoundLayers = {};
		this._tileLayersNum = 0;

		this.callInitHooks();

		this._addLayers(options.layers);
	},


	// public methods that modify map state

	// replaced by animation-powered implementation in Map.PanAnimation.js
	setView: function (center, zoom) {
		zoom = zoom === undefined ? this.getZoom() : zoom;
		this._resetView(L.latLng(center), this._limitZoom(zoom));
		return this;
	},

	setZoom: function (zoom, options) {
		if (!this._loaded) {
			this._zoom = this._limitZoom(zoom);
			return this;
		}
		return this.setView(this.getCenter(), zoom, {zoom: options});
	},

	zoomIn: function (delta, options) {
		return this.setZoom(this._zoom + (delta || 1), options);
	},

	zoomOut: function (delta, options) {
		return this.setZoom(this._zoom - (delta || 1), options);
	},

	setZoomAround: function (latlng, zoom, options) {
		var scale = this.getZoomScale(zoom),
		    viewHalf = this.getSize().divideBy(2),
		    containerPoint = latlng instanceof L.Point ? latlng : this.latLngToContainerPoint(latlng),

		    centerOffset = containerPoint.subtract(viewHalf).multiplyBy(1 - 1 / scale),
		    newCenter = this.containerPointToLatLng(viewHalf.add(centerOffset));

		return this.setView(newCenter, zoom, {zoom: options});
	},

	fitBounds: function (bounds, options) {

		options = options || {};
		bounds = bounds.getBounds ? bounds.getBounds() : L.latLngBounds(bounds);

		var paddingTL = L.point(options.paddingTopLeft || options.padding || [0, 0]),
		    paddingBR = L.point(options.paddingBottomRight || options.padding || [0, 0]),

		    zoom = this.getBoundsZoom(bounds, false, paddingTL.add(paddingBR));

		zoom = (options.maxZoom) ? Math.min(options.maxZoom, zoom) : zoom;

		var paddingOffset = paddingBR.subtract(paddingTL).divideBy(2),

		    swPoint = this.project(bounds.getSouthWest(), zoom),
		    nePoint = this.project(bounds.getNorthEast(), zoom),
		    center = this.unproject(swPoint.add(nePoint).divideBy(2).add(paddingOffset), zoom);

		return this.setView(center, zoom, options);
	},

	fitWorld: function (options) {
		return this.fitBounds([[-90, -180], [90, 180]], options);
	},

	panTo: function (center, options) { // (LatLng)
		return this.setView(center, this._zoom, {pan: options});
	},

	panBy: function (offset) { // (Point)
		// replaced with animated panBy in Map.PanAnimation.js
		this.fire('movestart');

		this._rawPanBy(L.point(offset));

		this.fire('move');
		return this.fire('moveend');
	},

	setMaxBounds: function (bounds) {
		bounds = L.latLngBounds(bounds);

		this.options.maxBounds = bounds;

		if (!bounds) {
			return this.off('moveend', this._panInsideMaxBounds, this);
		}

		if (this._loaded) {
			this._panInsideMaxBounds();
		}

		return this.on('moveend', this._panInsideMaxBounds, this);
	},

	panInsideBounds: function (bounds, options) {
		var center = this.getCenter(),
			newCenter = this._limitCenter(center, this._zoom, bounds);

		if (center.equals(newCenter)) { return this; }

		return this.panTo(newCenter, options);
	},

	addLayer: function (layer) {
		// TODO method is too big, refactor

		var id = L.stamp(layer);

		if (this._layers[id]) { return this; }

		this._layers[id] = layer;

		// TODO getMaxZoom, getMinZoom in ILayer (instead of options)
		if (layer.options && (!isNaN(layer.options.maxZoom) || !isNaN(layer.options.minZoom))) {
			this._zoomBoundLayers[id] = layer;
			this._updateZoomLevels();
		}

		// TODO looks ugly, refactor!!!
		if (this.options.zoomAnimation && L.TileLayer && (layer instanceof L.TileLayer)) {
			this._tileLayersNum++;
			this._tileLayersToLoad++;
			layer.on('load', this._onTileLayerLoad, this);
		}

		if (this._loaded) {
			this._layerAdd(layer);
		}

		return this;
	},

	removeLayer: function (layer) {
		var id = L.stamp(layer);

		if (!this._layers[id]) { return this; }

		if (this._loaded) {
			layer.onRemove(this);
		}

		delete this._layers[id];

		if (this._loaded) {
			this.fire('layerremove', {layer: layer});
		}

		if (this._zoomBoundLayers[id]) {
			delete this._zoomBoundLayers[id];
			this._updateZoomLevels();
		}

		// TODO looks ugly, refactor
		if (this.options.zoomAnimation && L.TileLayer && (layer instanceof L.TileLayer)) {
			this._tileLayersNum--;
			this._tileLayersToLoad--;
			layer.off('load', this._onTileLayerLoad, this);
		}

		return this;
	},

	hasLayer: function (layer) {
		if (!layer) { return false; }

		return (L.stamp(layer) in this._layers);
	},

	eachLayer: function (method, context) {
		for (var i in this._layers) {
			method.call(context, this._layers[i]);
		}
		return this;
	},

	invalidateSize: function (options) {
		if (!this._loaded) { return this; }

		options = L.extend({
			animate: false,
			pan: true
		}, options === true ? {animate: true} : options);

		var oldSize = this.getSize();
		this._sizeChanged = true;
		this._initialCenter = null;

		var newSize = this.getSize(),
		    oldCenter = oldSize.divideBy(2).round(),
		    newCenter = newSize.divideBy(2).round(),
		    offset = oldCenter.subtract(newCenter);

		if (!offset.x && !offset.y) { return this; }

		if (options.animate && options.pan) {
			this.panBy(offset);

		} else {
			if (options.pan) {
				this._rawPanBy(offset);
			}

			this.fire('move');

			if (options.debounceMoveend) {
				clearTimeout(this._sizeTimer);
				this._sizeTimer = setTimeout(L.bind(this.fire, this, 'moveend'), 200);
			} else {
				this.fire('moveend');
			}
		}

		return this.fire('resize', {
			oldSize: oldSize,
			newSize: newSize
		});
	},

	// TODO handler.addTo
	addHandler: function (name, HandlerClass) {
		if (!HandlerClass) { return this; }

		var handler = this[name] = new HandlerClass(this);

		this._handlers.push(handler);

		if (this.options[name]) {
			handler.enable();
		}

		return this;
	},

	remove: function () {
		if (this._loaded) {
			this.fire('unload');
		}

		this._initEvents('off');

		try {
			// throws error in IE6-8
			delete this._container._leaflet;
		} catch (e) {
			this._container._leaflet = undefined;
		}

		this._clearPanes();
		if (this._clearControlPos) {
			this._clearControlPos();
		}

		this._clearHandlers();

		return this;
	},


	// public methods for getting map state

	getCenter: function () { // (Boolean) -> LatLng
		this._checkIfLoaded();

		if (this._initialCenter && !this._moved()) {
			return this._initialCenter;
		}
		return this.layerPointToLatLng(this._getCenterLayerPoint());
	},

	getZoom: function () {
		return this._zoom;
	},

	getBounds: function () {
		var bounds = this.getPixelBounds(),
		    sw = this.unproject(bounds.getBottomLeft()),
		    ne = this.unproject(bounds.getTopRight());

		return new L.LatLngBounds(sw, ne);
	},

	getMinZoom: function () {
		return this.options.minZoom === undefined ?
			(this._layersMinZoom === undefined ? 0 : this._layersMinZoom) :
			this.options.minZoom;
	},

	getMaxZoom: function () {
		return this.options.maxZoom === undefined ?
			(this._layersMaxZoom === undefined ? Infinity : this._layersMaxZoom) :
			this.options.maxZoom;
	},

	getBoundsZoom: function (bounds, inside, padding) { // (LatLngBounds[, Boolean, Point]) -> Number
		bounds = L.latLngBounds(bounds);

		var zoom = this.getMinZoom() - (inside ? 1 : 0),
		    maxZoom = this.getMaxZoom(),
		    size = this.getSize(),

		    nw = bounds.getNorthWest(),
		    se = bounds.getSouthEast(),

		    zoomNotFound = true,
		    boundsSize;

		padding = L.point(padding || [0, 0]);

		do {
			zoom++;
			boundsSize = this.project(se, zoom).subtract(this.project(nw, zoom)).add(padding);
			zoomNotFound = !inside ? size.contains(boundsSize) : boundsSize.x < size.x || boundsSize.y < size.y;

		} while (zoomNotFound && zoom <= maxZoom);

		if (zoomNotFound && inside) {
			return null;
		}

		return inside ? zoom : zoom - 1;
	},

	getSize: function () {
		if (!this._size || this._sizeChanged) {
			this._size = new L.Point(
				this._container.clientWidth,
				this._container.clientHeight);

			this._sizeChanged = false;
		}
		return this._size.clone();
	},

	getPixelBounds: function () {
		var topLeftPoint = this._getTopLeftPoint();
		return new L.Bounds(topLeftPoint, topLeftPoint.add(this.getSize()));
	},

	getPixelOrigin: function () {
		this._checkIfLoaded();
		return this._initialTopLeftPoint;
	},

	getPanes: function () {
		return this._panes;
	},

	getContainer: function () {
		return this._container;
	},


	// TODO replace with universal implementation after refactoring projections

	getZoomScale: function (toZoom) {
		var crs = this.options.crs;
		return crs.scale(toZoom) / crs.scale(this._zoom);
	},

	getScaleZoom: function (scale) {
		return this._zoom + (Math.log(scale) / Math.LN2);
	},


	// conversion methods

	project: function (latlng, zoom) { // (LatLng[, Number]) -> Point
		zoom = zoom === undefined ? this._zoom : zoom;
		return this.options.crs.latLngToPoint(L.latLng(latlng), zoom);
	},

	unproject: function (point, zoom) { // (Point[, Number]) -> LatLng
		zoom = zoom === undefined ? this._zoom : zoom;
		return this.options.crs.pointToLatLng(L.point(point), zoom);
	},

	layerPointToLatLng: function (point) { // (Point)
		var projectedPoint = L.point(point).add(this.getPixelOrigin());
		return this.unproject(projectedPoint);
	},

	latLngToLayerPoint: function (latlng) { // (LatLng)
		var projectedPoint = this.project(L.latLng(latlng))._round();
		return projectedPoint._subtract(this.getPixelOrigin());
	},

	containerPointToLayerPoint: function (point) { // (Point)
		return L.point(point).subtract(this._getMapPanePos());
	},

	layerPointToContainerPoint: function (point) { // (Point)
		return L.point(point).add(this._getMapPanePos());
	},

	containerPointToLatLng: function (point) {
		var layerPoint = this.containerPointToLayerPoint(L.point(point));
		return this.layerPointToLatLng(layerPoint);
	},

	latLngToContainerPoint: function (latlng) {
		return this.layerPointToContainerPoint(this.latLngToLayerPoint(L.latLng(latlng)));
	},

	mouseEventToContainerPoint: function (e) { // (MouseEvent)
		return L.DomEvent.getMousePosition(e, this._container);
	},

	mouseEventToLayerPoint: function (e) { // (MouseEvent)
		return this.containerPointToLayerPoint(this.mouseEventToContainerPoint(e));
	},

	mouseEventToLatLng: function (e) { // (MouseEvent)
		return this.layerPointToLatLng(this.mouseEventToLayerPoint(e));
	},


	// map initialization methods

	_initContainer: function (id) {
		var container = this._container = L.DomUtil.get(id);

		if (!container) {
			throw new Error('Map container not found.');
		} else if (container._leaflet) {
			throw new Error('Map container is already initialized.');
		}

		container._leaflet = true;
	},

	_initLayout: function () {
		var container = this._container;

		L.DomUtil.addClass(container, 'leaflet-container' +
			(L.Browser.touch ? ' leaflet-touch' : '') +
			(L.Browser.retina ? ' leaflet-retina' : '') +
			(L.Browser.ielt9 ? ' leaflet-oldie' : '') +
			(this.options.fadeAnimation ? ' leaflet-fade-anim' : ''));

		var position = L.DomUtil.getStyle(container, 'position');

		if (position !== 'absolute' && position !== 'relative' && position !== 'fixed') {
			container.style.position = 'relative';
		}

		this._initPanes();

		if (this._initControlPos) {
			this._initControlPos();
		}
	},

	_initPanes: function () {
		var panes = this._panes = {};

		this._mapPane = panes.mapPane = this._createPane('leaflet-map-pane', this._container);

		this._tilePane = panes.tilePane = this._createPane('leaflet-tile-pane', this._mapPane);
		panes.objectsPane = this._createPane('leaflet-objects-pane', this._mapPane);
		panes.shadowPane = this._createPane('leaflet-shadow-pane');
		panes.overlayPane = this._createPane('leaflet-overlay-pane');
		panes.markerPane = this._createPane('leaflet-marker-pane');
		panes.popupPane = this._createPane('leaflet-popup-pane');

		var zoomHide = ' leaflet-zoom-hide';

		if (!this.options.markerZoomAnimation) {
			L.DomUtil.addClass(panes.markerPane, zoomHide);
			L.DomUtil.addClass(panes.shadowPane, zoomHide);
			L.DomUtil.addClass(panes.popupPane, zoomHide);
		}
	},

	_createPane: function (className, container) {
		return L.DomUtil.create('div', className, container || this._panes.objectsPane);
	},

	_clearPanes: function () {
		this._container.removeChild(this._mapPane);
	},

	_addLayers: function (layers) {
		layers = layers ? (L.Util.isArray(layers) ? layers : [layers]) : [];

		for (var i = 0, len = layers.length; i < len; i++) {
			this.addLayer(layers[i]);
		}
	},


	// private methods that modify map state

	_resetView: function (center, zoom, preserveMapOffset, afterZoomAnim) {

		var zoomChanged = (this._zoom !== zoom);

		if (!afterZoomAnim) {
			this.fire('movestart');

			if (zoomChanged) {
				this.fire('zoomstart');
			}
		}

		this._zoom = zoom;
		this._initialCenter = center;

		this._initialTopLeftPoint = this._getNewTopLeftPoint(center);

		if (!preserveMapOffset) {
			L.DomUtil.setPosition(this._mapPane, new L.Point(0, 0));
		} else {
			this._initialTopLeftPoint._add(this._getMapPanePos());
		}

		this._tileLayersToLoad = this._tileLayersNum;

		var loading = !this._loaded;
		this._loaded = true;

		this.fire('viewreset', {hard: !preserveMapOffset});

		if (loading) {
			this.fire('load');
			this.eachLayer(this._layerAdd, this);
		}

		this.fire('move');

		if (zoomChanged || afterZoomAnim) {
			this.fire('zoomend');
		}

		this.fire('moveend', {hard: !preserveMapOffset});
	},

	_rawPanBy: function (offset) {
		L.DomUtil.setPosition(this._mapPane, this._getMapPanePos().subtract(offset));
	},

	_getZoomSpan: function () {
		return this.getMaxZoom() - this.getMinZoom();
	},

	_updateZoomLevels: function () {
		var i,
			minZoom = Infinity,
			maxZoom = -Infinity,
			oldZoomSpan = this._getZoomSpan();

		for (i in this._zoomBoundLayers) {
			var layer = this._zoomBoundLayers[i];
			if (!isNaN(layer.options.minZoom)) {
				minZoom = Math.min(minZoom, layer.options.minZoom);
			}
			if (!isNaN(layer.options.maxZoom)) {
				maxZoom = Math.max(maxZoom, layer.options.maxZoom);
			}
		}

		if (i === undefined) { // we have no tilelayers
			this._layersMaxZoom = this._layersMinZoom = undefined;
		} else {
			this._layersMaxZoom = maxZoom;
			this._layersMinZoom = minZoom;
		}

		if (oldZoomSpan !== this._getZoomSpan()) {
			this.fire('zoomlevelschange');
		}
	},

	_panInsideMaxBounds: function () {
		this.panInsideBounds(this.options.maxBounds);
	},

	_checkIfLoaded: function () {
		if (!this._loaded) {
			throw new Error('Set map center and zoom first.');
		}
	},

	// map events

	_initEvents: function (onOff) {
		if (!L.DomEvent) { return; }

		onOff = onOff || 'on';

		L.DomEvent[onOff](this._container, 'click', this._onMouseClick, this);

		var events = ['dblclick', 'mousedown', 'mouseup', 'mouseenter',
		              'mouseleave', 'mousemove', 'contextmenu'],
		    i, len;

		for (i = 0, len = events.length; i < len; i++) {
			L.DomEvent[onOff](this._container, events[i], this._fireMouseEvent, this);
		}

		if (this.options.trackResize) {
			L.DomEvent[onOff](window, 'resize', this._onResize, this);
		}
	},

	_onResize: function () {
		L.Util.cancelAnimFrame(this._resizeRequest);
		this._resizeRequest = L.Util.requestAnimFrame(
		        function () { this.invalidateSize({debounceMoveend: true}); }, this, false, this._container);
	},

	_onMouseClick: function (e) {
		if (!this._loaded || (!e._simulated &&
		        ((this.dragging && this.dragging.moved()) ||
		         (this.boxZoom  && this.boxZoom.moved()))) ||
		            L.DomEvent._skipped(e)) { return; }

		this.fire('preclick');
		this._fireMouseEvent(e);
	},

	_fireMouseEvent: function (e) {
		if (!this._loaded || L.DomEvent._skipped(e)) { return; }

		var type = e.type;

		type = (type === 'mouseenter' ? 'mouseover' : (type === 'mouseleave' ? 'mouseout' : type));

		if (!this.hasEventListeners(type)) { return; }

		if (type === 'contextmenu') {
			L.DomEvent.preventDefault(e);
		}

		var containerPoint = this.mouseEventToContainerPoint(e),
		    layerPoint = this.containerPointToLayerPoint(containerPoint),
		    latlng = this.layerPointToLatLng(layerPoint);

		this.fire(type, {
			latlng: latlng,
			layerPoint: layerPoint,
			containerPoint: containerPoint,
			originalEvent: e
		});
	},

	_onTileLayerLoad: function () {
		this._tileLayersToLoad--;
		if (this._tileLayersNum && !this._tileLayersToLoad) {
			this.fire('tilelayersload');
		}
	},

	_clearHandlers: function () {
		for (var i = 0, len = this._handlers.length; i < len; i++) {
			this._handlers[i].disable();
		}
	},

	whenReady: function (callback, context) {
		if (this._loaded) {
			callback.call(context || this, this);
		} else {
			this.on('load', callback, context);
		}
		return this;
	},

	_layerAdd: function (layer) {
		layer.onAdd(this);
		this.fire('layeradd', {layer: layer});
	},


	// private methods for getting map state

	_getMapPanePos: function () {
		return L.DomUtil.getPosition(this._mapPane);
	},

	_moved: function () {
		var pos = this._getMapPanePos();
		return pos && !pos.equals([0, 0]);
	},

	_getTopLeftPoint: function () {
		return this.getPixelOrigin().subtract(this._getMapPanePos());
	},

	_getNewTopLeftPoint: function (center, zoom) {
		var viewHalf = this.getSize()._divideBy(2);
		// TODO round on display, not calculation to increase precision?
		return this.project(center, zoom)._subtract(viewHalf)._round();
	},

	_latLngToNewLayerPoint: function (latlng, newZoom, newCenter) {
		var topLeft = this._getNewTopLeftPoint(newCenter, newZoom).add(this._getMapPanePos());
		return this.project(latlng, newZoom)._subtract(topLeft);
	},

	// layer point of the current center
	_getCenterLayerPoint: function () {
		return this.containerPointToLayerPoint(this.getSize()._divideBy(2));
	},

	// offset of the specified place to the current center in pixels
	_getCenterOffset: function (latlng) {
		return this.latLngToLayerPoint(latlng).subtract(this._getCenterLayerPoint());
	},

	// adjust center for view to get inside bounds
	_limitCenter: function (center, zoom, bounds) {

		if (!bounds) { return center; }

		var centerPoint = this.project(center, zoom),
		    viewHalf = this.getSize().divideBy(2),
		    viewBounds = new L.Bounds(centerPoint.subtract(viewHalf), centerPoint.add(viewHalf)),
		    offset = this._getBoundsOffset(viewBounds, bounds, zoom);

		return this.unproject(centerPoint.add(offset), zoom);
	},

	// adjust offset for view to get inside bounds
	_limitOffset: function (offset, bounds) {
		if (!bounds) { return offset; }

		var viewBounds = this.getPixelBounds(),
		    newBounds = new L.Bounds(viewBounds.min.add(offset), viewBounds.max.add(offset));

		return offset.add(this._getBoundsOffset(newBounds, bounds));
	},

	// returns offset needed for pxBounds to get inside maxBounds at a specified zoom
	_getBoundsOffset: function (pxBounds, maxBounds, zoom) {
		var nwOffset = this.project(maxBounds.getNorthWest(), zoom).subtract(pxBounds.min),
		    seOffset = this.project(maxBounds.getSouthEast(), zoom).subtract(pxBounds.max),

		    dx = this._rebound(nwOffset.x, -seOffset.x),
		    dy = this._rebound(nwOffset.y, -seOffset.y);

		return new L.Point(dx, dy);
	},

	_rebound: function (left, right) {
		return left + right > 0 ?
			Math.round(left - right) / 2 :
			Math.max(0, Math.ceil(left)) - Math.max(0, Math.floor(right));
	},

	_limitZoom: function (zoom) {
		var min = this.getMinZoom(),
		    max = this.getMaxZoom();

		return Math.max(min, Math.min(max, zoom));
	}
});

L.map = function (id, options) {
	return new L.Map(id, options);
};


/*
 * Mercator projection that takes into account that the Earth is not a perfect sphere.
 * Less popular than spherical mercator; used by projections like EPSG:3395.
 */

L.Projection.Mercator = {
	MAX_LATITUDE: 85.0840591556,

	R_MINOR: 6356752.314245179,
	R_MAJOR: 6378137,

	project: function (latlng) { // (LatLng) -> Point
		var d = L.LatLng.DEG_TO_RAD,
		    max = this.MAX_LATITUDE,
		    lat = Math.max(Math.min(max, latlng.lat), -max),
		    r = this.R_MAJOR,
		    r2 = this.R_MINOR,
		    x = latlng.lng * d * r,
		    y = lat * d,
		    tmp = r2 / r,
		    eccent = Math.sqrt(1.0 - tmp * tmp),
		    con = eccent * Math.sin(y);

		con = Math.pow((1 - con) / (1 + con), eccent * 0.5);

		var ts = Math.tan(0.5 * ((Math.PI * 0.5) - y)) / con;
		y = -r * Math.log(ts);

		return new L.Point(x, y);
	},

	unproject: function (point) { // (Point, Boolean) -> LatLng
		var d = L.LatLng.RAD_TO_DEG,
		    r = this.R_MAJOR,
		    r2 = this.R_MINOR,
		    lng = point.x * d / r,
		    tmp = r2 / r,
		    eccent = Math.sqrt(1 - (tmp * tmp)),
		    ts = Math.exp(- point.y / r),
		    phi = (Math.PI / 2) - 2 * Math.atan(ts),
		    numIter = 15,
		    tol = 1e-7,
		    i = numIter,
		    dphi = 0.1,
		    con;

		while ((Math.abs(dphi) > tol) && (--i > 0)) {
			con = eccent * Math.sin(phi);
			dphi = (Math.PI / 2) - 2 * Math.atan(ts *
			            Math.pow((1.0 - con) / (1.0 + con), 0.5 * eccent)) - phi;
			phi += dphi;
		}

		return new L.LatLng(phi * d, lng);
	}
};



L.CRS.EPSG3395 = L.extend({}, L.CRS, {
	code: 'EPSG:3395',

	projection: L.Projection.Mercator,

	transformation: (function () {
		var m = L.Projection.Mercator,
		    r = m.R_MAJOR,
		    scale = 0.5 / (Math.PI * r);

		return new L.Transformation(scale, 0.5, -scale, 0.5);
	}())
});


/*
 * L.TileLayer is used for standard xyz-numbered tile layers.
 */

L.TileLayer = L.Class.extend({
	includes: L.Mixin.Events,

	options: {
		minZoom: 0,
		maxZoom: 18,
		tileSize: 256,
		subdomains: 'abc',
		errorTileUrl: '',
		attribution: '',
		zoomOffset: 0,
		opacity: 1,
		/*
		maxNativeZoom: null,
		zIndex: null,
		tms: false,
		continuousWorld: false,
		noWrap: false,
		zoomReverse: false,
		detectRetina: false,
		reuseTiles: false,
		bounds: false,
		*/
		unloadInvisibleTiles: L.Browser.mobile,
		updateWhenIdle: L.Browser.mobile
	},

	initialize: function (url, options) {
		options = L.setOptions(this, options);

		// detecting retina displays, adjusting tileSize and zoom levels
		if (options.detectRetina && L.Browser.retina && options.maxZoom > 0) {

			options.tileSize = Math.floor(options.tileSize / 2);
			options.zoomOffset++;

			if (options.minZoom > 0) {
				options.minZoom--;
			}
			this.options.maxZoom--;
		}

		if (options.bounds) {
			options.bounds = L.latLngBounds(options.bounds);
		}

		this._url = url;

		var subdomains = this.options.subdomains;

		if (typeof subdomains === 'string') {
			this.options.subdomains = subdomains.split('');
		}
	},

	onAdd: function (map) {
		this._map = map;
		this._animated = map._zoomAnimated;

		// create a container div for tiles
		this._initContainer();

		// set up events
		map.on({
			'viewreset': this._reset,
			'moveend': this._update
		}, this);

		if (this._animated) {
			map.on({
				'zoomanim': this._animateZoom,
				'zoomend': this._endZoomAnim
			}, this);
		}

		if (!this.options.updateWhenIdle) {
			this._limitedUpdate = L.Util.limitExecByInterval(this._update, 150, this);
			map.on('move', this._limitedUpdate, this);
		}

		this._reset();
		this._update();
	},

	addTo: function (map) {
		map.addLayer(this);
		return this;
	},

	onRemove: function (map) {
		this._container.parentNode.removeChild(this._container);

		map.off({
			'viewreset': this._reset,
			'moveend': this._update
		}, this);

		if (this._animated) {
			map.off({
				'zoomanim': this._animateZoom,
				'zoomend': this._endZoomAnim
			}, this);
		}

		if (!this.options.updateWhenIdle) {
			map.off('move', this._limitedUpdate, this);
		}

		this._container = null;
		this._map = null;
	},

	bringToFront: function () {
		var pane = this._map._panes.tilePane;

		if (this._container) {
			pane.appendChild(this._container);
			this._setAutoZIndex(pane, Math.max);
		}

		return this;
	},

	bringToBack: function () {
		var pane = this._map._panes.tilePane;

		if (this._container) {
			pane.insertBefore(this._container, pane.firstChild);
			this._setAutoZIndex(pane, Math.min);
		}

		return this;
	},

	getAttribution: function () {
		return this.options.attribution;
	},

	getContainer: function () {
		return this._container;
	},

	setOpacity: function (opacity) {
		this.options.opacity = opacity;

		if (this._map) {
			this._updateOpacity();
		}

		return this;
	},

	setZIndex: function (zIndex) {
		this.options.zIndex = zIndex;
		this._updateZIndex();

		return this;
	},

	setUrl: function (url, noRedraw) {
		this._url = url;

		if (!noRedraw) {
			this.redraw();
		}

		return this;
	},

	redraw: function () {
		if (this._map) {
			this._reset({hard: true});
			this._update();
		}
		return this;
	},

	_updateZIndex: function () {
		if (this._container && this.options.zIndex !== undefined) {
			this._container.style.zIndex = this.options.zIndex;
		}
	},

	_setAutoZIndex: function (pane, compare) {

		var layers = pane.children,
		    edgeZIndex = -compare(Infinity, -Infinity), // -Infinity for max, Infinity for min
		    zIndex, i, len;

		for (i = 0, len = layers.length; i < len; i++) {

			if (layers[i] !== this._container) {
				zIndex = parseInt(layers[i].style.zIndex, 10);

				if (!isNaN(zIndex)) {
					edgeZIndex = compare(edgeZIndex, zIndex);
				}
			}
		}

		this.options.zIndex = this._container.style.zIndex =
		        (isFinite(edgeZIndex) ? edgeZIndex : 0) + compare(1, -1);
	},

	_updateOpacity: function () {
		var i,
		    tiles = this._tiles;

		if (L.Browser.ielt9) {
			for (i in tiles) {
				L.DomUtil.setOpacity(tiles[i], this.options.opacity);
			}
		} else {
			L.DomUtil.setOpacity(this._container, this.options.opacity);
		}
	},

	_initContainer: function () {
		var tilePane = this._map._panes.tilePane;

		if (!this._container) {
			this._container = L.DomUtil.create('div', 'leaflet-layer');

			this._updateZIndex();

			if (this._animated) {
				var className = 'leaflet-tile-container';

				this._bgBuffer = L.DomUtil.create('div', className, this._container);
				this._tileContainer = L.DomUtil.create('div', className, this._container);

			} else {
				this._tileContainer = this._container;
			}

			tilePane.appendChild(this._container);

			if (this.options.opacity < 1) {
				this._updateOpacity();
			}
		}
	},

	_reset: function (e) {
		for (var key in this._tiles) {
			this.fire('tileunload', {tile: this._tiles[key]});
		}

		this._tiles = {};
		this._tilesToLoad = 0;

		if (this.options.reuseTiles) {
			this._unusedTiles = [];
		}

		this._tileContainer.innerHTML = '';

		if (this._animated && e && e.hard) {
			this._clearBgBuffer();
		}

		this._initContainer();
	},

	_getTileSize: function () {
		var map = this._map,
		    zoom = map.getZoom() + this.options.zoomOffset,
		    zoomN = this.options.maxNativeZoom,
		    tileSize = this.options.tileSize;

		if (zoomN && zoom > zoomN) {
			tileSize = Math.round(map.getZoomScale(zoom) / map.getZoomScale(zoomN) * tileSize);
		}

		return tileSize;
	},

	_update: function () {

		if (!this._map) { return; }

		var map = this._map,
		    bounds = map.getPixelBounds(),
		    zoom = map.getZoom(),
		    tileSize = this._getTileSize();

		if (zoom > this.options.maxZoom || zoom < this.options.minZoom) {
			return;
		}

		var tileBounds = L.bounds(
		        bounds.min.divideBy(tileSize)._floor(),
		        bounds.max.divideBy(tileSize)._floor());

		this._addTilesFromCenterOut(tileBounds);

		if (this.options.unloadInvisibleTiles || this.options.reuseTiles) {
			this._removeOtherTiles(tileBounds);
		}
	},

	_addTilesFromCenterOut: function (bounds) {
		var queue = [],
		    center = bounds.getCenter();

		var j, i, point;

		for (j = bounds.min.y; j <= bounds.max.y; j++) {
			for (i = bounds.min.x; i <= bounds.max.x; i++) {
				point = new L.Point(i, j);

				if (this._tileShouldBeLoaded(point)) {
					queue.push(point);
				}
			}
		}

		var tilesToLoad = queue.length;

		if (tilesToLoad === 0) { return; }

		// load tiles in order of their distance to center
		queue.sort(function (a, b) {
			return a.distanceTo(center) - b.distanceTo(center);
		});

		var fragment = document.createDocumentFragment();

		// if its the first batch of tiles to load
		if (!this._tilesToLoad) {
			this.fire('loading');
		}

		this._tilesToLoad += tilesToLoad;

		for (i = 0; i < tilesToLoad; i++) {
			this._addTile(queue[i], fragment);
		}

		this._tileContainer.appendChild(fragment);
	},

	_tileShouldBeLoaded: function (tilePoint) {
		if ((tilePoint.x + ':' + tilePoint.y) in this._tiles) {
			return false; // already loaded
		}

		var options = this.options;

		if (!options.continuousWorld) {
			var limit = this._getWrapTileNum();

			// don't load if exceeds world bounds
			if ((options.noWrap && (tilePoint.x < 0 || tilePoint.x >= limit.x)) ||
				tilePoint.y < 0 || tilePoint.y >= limit.y) { return false; }
		}

		if (options.bounds) {
			var tileSize = this._getTileSize(),
			    nwPoint = tilePoint.multiplyBy(tileSize),
			    sePoint = nwPoint.add([tileSize, tileSize]),
			    nw = this._map.unproject(nwPoint),
			    se = this._map.unproject(sePoint);

			// TODO temporary hack, will be removed after refactoring projections
			// https://github.com/Leaflet/Leaflet/issues/1618
			if (!options.continuousWorld && !options.noWrap) {
				nw = nw.wrap();
				se = se.wrap();
			}

			if (!options.bounds.intersects([nw, se])) { return false; }
		}

		return true;
	},

	_removeOtherTiles: function (bounds) {
		var kArr, x, y, key;

		for (key in this._tiles) {
			kArr = key.split(':');
			x = parseInt(kArr[0], 10);
			y = parseInt(kArr[1], 10);

			// remove tile if it's out of bounds
			if (x < bounds.min.x || x > bounds.max.x || y < bounds.min.y || y > bounds.max.y) {
				this._removeTile(key);
			}
		}
	},

	_removeTile: function (key) {
		var tile = this._tiles[key];

		this.fire('tileunload', {tile: tile, url: tile.src});

		if (this.options.reuseTiles) {
			L.DomUtil.removeClass(tile, 'leaflet-tile-loaded');
			this._unusedTiles.push(tile);

		} else if (tile.parentNode === this._tileContainer) {
			this._tileContainer.removeChild(tile);
		}

		// for https://github.com/CloudMade/Leaflet/issues/137
		if (!L.Browser.android) {
			tile.onload = null;
			tile.src = L.Util.emptyImageUrl;
		}

		delete this._tiles[key];
	},

	_addTile: function (tilePoint, container) {
		var tilePos = this._getTilePos(tilePoint);

		// get unused tile - or create a new tile
		var tile = this._getTile();

		/*
		Chrome 20 layouts much faster with top/left (verify with timeline, frames)
		Android 4 browser has display issues with top/left and requires transform instead
		(other browsers don't currently care) - see debug/hacks/jitter.html for an example
		*/
		L.DomUtil.setPosition(tile, tilePos, L.Browser.chrome);

		this._tiles[tilePoint.x + ':' + tilePoint.y] = tile;

		this._loadTile(tile, tilePoint);

		if (tile.parentNode !== this._tileContainer) {
			container.appendChild(tile);
		}
	},

	_getZoomForUrl: function () {

		var options = this.options,
		    zoom = this._map.getZoom();

		if (options.zoomReverse) {
			zoom = options.maxZoom - zoom;
		}

		zoom += options.zoomOffset;

		return options.maxNativeZoom ? Math.min(zoom, options.maxNativeZoom) : zoom;
	},

	_getTilePos: function (tilePoint) {
		var origin = this._map.getPixelOrigin(),
		    tileSize = this._getTileSize();

		return tilePoint.multiplyBy(tileSize).subtract(origin);
	},

	// image-specific code (override to implement e.g. Canvas or SVG tile layer)

	getTileUrl: function (tilePoint) {
		return L.Util.template(this._url, L.extend({
			s: this._getSubdomain(tilePoint),
			z: tilePoint.z,
			x: tilePoint.x,
			y: tilePoint.y
		}, this.options));
	},

	_getWrapTileNum: function () {
		var crs = this._map.options.crs,
		    size = crs.getSize(this._map.getZoom());
		return size.divideBy(this._getTileSize())._floor();
	},

	_adjustTilePoint: function (tilePoint) {

		var limit = this._getWrapTileNum();

		// wrap tile coordinates
		if (!this.options.continuousWorld && !this.options.noWrap) {
			tilePoint.x = ((tilePoint.x % limit.x) + limit.x) % limit.x;
		}

		if (this.options.tms) {
			tilePoint.y = limit.y - tilePoint.y - 1;
		}

		tilePoint.z = this._getZoomForUrl();
	},

	_getSubdomain: function (tilePoint) {
		var index = Math.abs(tilePoint.x + tilePoint.y) % this.options.subdomains.length;
		return this.options.subdomains[index];
	},

	_getTile: function () {
		if (this.options.reuseTiles && this._unusedTiles.length > 0) {
			var tile = this._unusedTiles.pop();
			this._resetTile(tile);
			return tile;
		}
		return this._createTile();
	},

	// Override if data stored on a tile needs to be cleaned up before reuse
	_resetTile: function (/*tile*/) {},

	_createTile: function () {
		var tile = L.DomUtil.create('img', 'leaflet-tile');
		tile.style.width = tile.style.height = this._getTileSize() + 'px';
		tile.galleryimg = 'no';

		tile.onselectstart = tile.onmousemove = L.Util.falseFn;

		if (L.Browser.ielt9 && this.options.opacity !== undefined) {
			L.DomUtil.setOpacity(tile, this.options.opacity);
		}
		// without this hack, tiles disappear after zoom on Chrome for Android
		// https://github.com/Leaflet/Leaflet/issues/2078
		if (L.Browser.mobileWebkit3d) {
			tile.style.WebkitBackfaceVisibility = 'hidden';
		}
		return tile;
	},

	_loadTile: function (tile, tilePoint) {
		tile._layer  = this;
		tile.onload  = this._tileOnLoad;
		tile.onerror = this._tileOnError;

		this._adjustTilePoint(tilePoint);
		tile.src     = this.getTileUrl(tilePoint);

		this.fire('tileloadstart', {
			tile: tile,
			url: tile.src
		});
	},

	_tileLoaded: function () {
		this._tilesToLoad--;

		if (this._animated) {
			L.DomUtil.addClass(this._tileContainer, 'leaflet-zoom-animated');
		}

		if (!this._tilesToLoad) {
			this.fire('load');

			if (this._animated) {
				// clear scaled tiles after all new tiles are loaded (for performance)
				clearTimeout(this._clearBgBufferTimer);
				this._clearBgBufferTimer = setTimeout(L.bind(this._clearBgBuffer, this), 500);
			}
		}
	},

	_tileOnLoad: function () {
		var layer = this._layer;

		//Only if we are loading an actual image
		if (this.src !== L.Util.emptyImageUrl) {
			L.DomUtil.addClass(this, 'leaflet-tile-loaded');

			layer.fire('tileload', {
				tile: this,
				url: this.src
			});
		}

		layer._tileLoaded();
	},

	_tileOnError: function () {
		var layer = this._layer;

		layer.fire('tileerror', {
			tile: this,
			url: this.src
		});

		var newUrl = layer.options.errorTileUrl;
		if (newUrl) {
			this.src = newUrl;
		}

		layer._tileLoaded();
	}
});

L.tileLayer = function (url, options) {
	return new L.TileLayer(url, options);
};


/*
 * L.TileLayer.WMS is used for putting WMS tile layers on the map.
 */

L.TileLayer.WMS = L.TileLayer.extend({

	defaultWmsParams: {
		service: 'WMS',
		request: 'GetMap',
		version: '1.1.1',
		layers: '',
		styles: '',
		format: 'image/jpeg',
		transparent: false
	},

	initialize: function (url, options) { // (String, Object)

		this._url = url;

		var wmsParams = L.extend({}, this.defaultWmsParams),
		    tileSize = options.tileSize || this.options.tileSize;

		if (options.detectRetina && L.Browser.retina) {
			wmsParams.width = wmsParams.height = tileSize * 2;
		} else {
			wmsParams.width = wmsParams.height = tileSize;
		}

		for (var i in options) {
			// all keys that are not TileLayer options go to WMS params
			if (!this.options.hasOwnProperty(i) && i !== 'crs') {
				wmsParams[i] = options[i];
			}
		}

		this.wmsParams = wmsParams;

		L.setOptions(this, options);
	},

	onAdd: function (map) {

		this._crs = this.options.crs || map.options.crs;

		this._wmsVersion = parseFloat(this.wmsParams.version);

		var projectionKey = this._wmsVersion >= 1.3 ? 'crs' : 'srs';
		this.wmsParams[projectionKey] = this._crs.code;

		L.TileLayer.prototype.onAdd.call(this, map);
	},

	getTileUrl: function (tilePoint) { // (Point, Number) -> String

		var map = this._map,
		    tileSize = this.options.tileSize,

		    nwPoint = tilePoint.multiplyBy(tileSize),
		    sePoint = nwPoint.add([tileSize, tileSize]),

		    nw = this._crs.project(map.unproject(nwPoint, tilePoint.z)),
		    se = this._crs.project(map.unproject(sePoint, tilePoint.z)),
		    bbox = this._wmsVersion >= 1.3 && this._crs === L.CRS.EPSG4326 ?
		        [se.y, nw.x, nw.y, se.x].join(',') :
		        [nw.x, se.y, se.x, nw.y].join(','),

		    url = L.Util.template(this._url, {s: this._getSubdomain(tilePoint)});

		return url + L.Util.getParamString(this.wmsParams, url, true) + '&BBOX=' + bbox;
	},

	setParams: function (params, noRedraw) {

		L.extend(this.wmsParams, params);

		if (!noRedraw) {
			this.redraw();
		}

		return this;
	}
});

L.tileLayer.wms = function (url, options) {
	return new L.TileLayer.WMS(url, options);
};


/*
 * L.TileLayer.Canvas is a class that you can use as a base for creating
 * dynamically drawn Canvas-based tile layers.
 */

L.TileLayer.Canvas = L.TileLayer.extend({
	options: {
		async: false
	},

	initialize: function (options) {
		L.setOptions(this, options);
	},

	redraw: function () {
		if (this._map) {
			this._reset({hard: true});
			this._update();
		}

		for (var i in this._tiles) {
			this._redrawTile(this._tiles[i]);
		}
		return this;
	},

	_redrawTile: function (tile) {
		this.drawTile(tile, tile._tilePoint, this._map._zoom);
	},

	_createTile: function () {
		var tile = L.DomUtil.create('canvas', 'leaflet-tile');
		tile.width = tile.height = this.options.tileSize;
		tile.onselectstart = tile.onmousemove = L.Util.falseFn;
		return tile;
	},

	_loadTile: function (tile, tilePoint) {
		tile._layer = this;
		tile._tilePoint = tilePoint;

		this._redrawTile(tile);

		if (!this.options.async) {
			this.tileDrawn(tile);
		}
	},

	drawTile: function (/*tile, tilePoint*/) {
		// override with rendering code
	},

	tileDrawn: function (tile) {
		this._tileOnLoad.call(tile);
	}
});


L.tileLayer.canvas = function (options) {
	return new L.TileLayer.Canvas(options);
};


/*
 * L.ImageOverlay is used to overlay images over the map (to specific geographical bounds).
 */

L.ImageOverlay = L.Class.extend({
	includes: L.Mixin.Events,

	options: {
		opacity: 1
	},

	initialize: function (url, bounds, options) { // (String, LatLngBounds, Object)
		this._url = url;
		this._bounds = L.latLngBounds(bounds);

		L.setOptions(this, options);
	},

	onAdd: function (map) {
		this._map = map;

		if (!this._image) {
			this._initImage();
		}

		map._panes.overlayPane.appendChild(this._image);

		map.on('viewreset', this._reset, this);

		if (map.options.zoomAnimation && L.Browser.any3d) {
			map.on('zoomanim', this._animateZoom, this);
		}

		this._reset();
	},

	onRemove: function (map) {
		map.getPanes().overlayPane.removeChild(this._image);

		map.off('viewreset', this._reset, this);

		if (map.options.zoomAnimation) {
			map.off('zoomanim', this._animateZoom, this);
		}
	},

	addTo: function (map) {
		map.addLayer(this);
		return this;
	},

	setOpacity: function (opacity) {
		this.options.opacity = opacity;
		this._updateOpacity();
		return this;
	},

	// TODO remove bringToFront/bringToBack duplication from TileLayer/Path
	bringToFront: function () {
		if (this._image) {
			this._map._panes.overlayPane.appendChild(this._image);
		}
		return this;
	},

	bringToBack: function () {
		var pane = this._map._panes.overlayPane;
		if (this._image) {
			pane.insertBefore(this._image, pane.firstChild);
		}
		return this;
	},

	setUrl: function (url) {
		this._url = url;
		this._image.src = this._url;
	},

	getAttribution: function () {
		return this.options.attribution;
	},

	_initImage: function () {
		this._image = L.DomUtil.create('img', 'leaflet-image-layer');

		if (this._map.options.zoomAnimation && L.Browser.any3d) {
			L.DomUtil.addClass(this._image, 'leaflet-zoom-animated');
		} else {
			L.DomUtil.addClass(this._image, 'leaflet-zoom-hide');
		}

		this._updateOpacity();

		//TODO createImage util method to remove duplication
		L.extend(this._image, {
			galleryimg: 'no',
			onselectstart: L.Util.falseFn,
			onmousemove: L.Util.falseFn,
			onload: L.bind(this._onImageLoad, this),
			src: this._url
		});
	},

	_animateZoom: function (e) {
		var map = this._map,
		    image = this._image,
		    scale = map.getZoomScale(e.zoom),
		    nw = this._bounds.getNorthWest(),
		    se = this._bounds.getSouthEast(),

		    topLeft = map._latLngToNewLayerPoint(nw, e.zoom, e.center),
		    size = map._latLngToNewLayerPoint(se, e.zoom, e.center)._subtract(topLeft),
		    origin = topLeft._add(size._multiplyBy((1 / 2) * (1 - 1 / scale)));

		image.style[L.DomUtil.TRANSFORM] =
		        L.DomUtil.getTranslateString(origin) + ' scale(' + scale + ') ';
	},

	_reset: function () {
		var image   = this._image,
		    topLeft = this._map.latLngToLayerPoint(this._bounds.getNorthWest()),
		    size = this._map.latLngToLayerPoint(this._bounds.getSouthEast())._subtract(topLeft);

		L.DomUtil.setPosition(image, topLeft);

		image.style.width  = size.x + 'px';
		image.style.height = size.y + 'px';
	},

	_onImageLoad: function () {
		this.fire('load');
	},

	_updateOpacity: function () {
		L.DomUtil.setOpacity(this._image, this.options.opacity);
	}
});

L.imageOverlay = function (url, bounds, options) {
	return new L.ImageOverlay(url, bounds, options);
};


/*
 * L.Icon is an image-based icon class that you can use with L.Marker for custom markers.
 */

L.Icon = L.Class.extend({
	options: {
		/*
		iconUrl: (String) (required)
		iconRetinaUrl: (String) (optional, used for retina devices if detected)
		iconSize: (Point) (can be set through CSS)
		iconAnchor: (Point) (centered by default, can be set in CSS with negative margins)
		popupAnchor: (Point) (if not specified, popup opens in the anchor point)
		shadowUrl: (String) (no shadow by default)
		shadowRetinaUrl: (String) (optional, used for retina devices if detected)
		shadowSize: (Point)
		shadowAnchor: (Point)
		*/
		className: ''
	},

	initialize: function (options) {
		L.setOptions(this, options);
	},

	createIcon: function (oldIcon) {
		return this._createIcon('icon', oldIcon);
	},

	createShadow: function (oldIcon) {
		return this._createIcon('shadow', oldIcon);
	},

	_createIcon: function (name, oldIcon) {
		var src = this._getIconUrl(name);

		if (!src) {
			if (name === 'icon') {
				throw new Error('iconUrl not set in Icon options (see the docs).');
			}
			return null;
		}

		var img;
		if (!oldIcon || oldIcon.tagName !== 'IMG') {
			img = this._createImg(src);
		} else {
			img = this._createImg(src, oldIcon);
		}
		this._setIconStyles(img, name);

		return img;
	},

	_setIconStyles: function (img, name) {
		var options = this.options,
		    size = L.point(options[name + 'Size']),
		    anchor;

		if (name === 'shadow') {
			anchor = L.point(options.shadowAnchor || options.iconAnchor);
		} else {
			anchor = L.point(options.iconAnchor);
		}

		if (!anchor && size) {
			anchor = size.divideBy(2, true);
		}

		img.className = 'leaflet-marker-' + name + ' ' + options.className;

		if (anchor) {
			img.style.marginLeft = (-anchor.x) + 'px';
			img.style.marginTop  = (-anchor.y) + 'px';
		}

		if (size) {
			img.style.width  = size.x + 'px';
			img.style.height = size.y + 'px';
		}
	},

	_createImg: function (src, el) {
		el = el || document.createElement('img');
		el.src = src;
		return el;
	},

	_getIconUrl: function (name) {
		if (L.Browser.retina && this.options[name + 'RetinaUrl']) {
			return this.options[name + 'RetinaUrl'];
		}
		return this.options[name + 'Url'];
	}
});

L.icon = function (options) {
	return new L.Icon(options);
};


/*
 * L.Icon.Default is the blue marker icon used by default in Leaflet.
 */

L.Icon.Default = L.Icon.extend({

	options: {
		iconSize: [25, 41],
		iconAnchor: [12, 41],
		popupAnchor: [1, -34],

		shadowSize: [41, 41]
	},

	_getIconUrl: function (name) {
		var key = name + 'Url';

		if (this.options[key]) {
			return this.options[key];
		}

		if (L.Browser.retina && name === 'icon') {
			name += '-2x';
		}

		var path = L.Icon.Default.imagePath;

		if (!path) {
			throw new Error('Couldn\'t autodetect L.Icon.Default.imagePath, set it manually.');
		}

		return path + '/marker-' + name + '.png';
	}
});

L.Icon.Default.imagePath = (function () {
	var scripts = document.getElementsByTagName('script'),
	    leafletRe = /[\/^]leaflet[\-\._]?([\w\-\._]*)\.js\??/;

	var i, len, src, matches, path;

	for (i = 0, len = scripts.length; i < len; i++) {
		src = scripts[i].src;
		matches = src.match(leafletRe);

		if (matches) {
			path = src.split(leafletRe)[0];
			return (path ? path + '/' : '') + 'images';
		}
	}
}());


/*
 * L.Marker is used to display clickable/draggable icons on the map.
 */

L.Marker = L.Class.extend({

	includes: L.Mixin.Events,

	options: {
		icon: new L.Icon.Default(),
		title: '',
		alt: '',
		clickable: true,
		draggable: false,
		keyboard: true,
		zIndexOffset: 0,
		opacity: 1,
		riseOnHover: false,
		riseOffset: 250
	},

	initialize: function (latlng, options) {
		L.setOptions(this, options);
		this._latlng = L.latLng(latlng);
	},

	onAdd: function (map) {
		this._map = map;

		map.on('viewreset', this.update, this);

		this._initIcon();
		this.update();
		this.fire('add');

		if (map.options.zoomAnimation && map.options.markerZoomAnimation) {
			map.on('zoomanim', this._animateZoom, this);
		}
	},

	addTo: function (map) {
		map.addLayer(this);
		return this;
	},

	onRemove: function (map) {
		if (this.dragging) {
			this.dragging.disable();
		}

		this._removeIcon();
		this._removeShadow();

		this.fire('remove');

		map.off({
			'viewreset': this.update,
			'zoomanim': this._animateZoom
		}, this);

		this._map = null;
	},

	getLatLng: function () {
		return this._latlng;
	},

	setLatLng: function (latlng) {
		this._latlng = L.latLng(latlng);

		this.update();

		return this.fire('move', { latlng: this._latlng });
	},

	setZIndexOffset: function (offset) {
		this.options.zIndexOffset = offset;
		this.update();

		return this;
	},

	setIcon: function (icon) {

		this.options.icon = icon;

		if (this._map) {
			this._initIcon();
			this.update();
		}

		if (this._popup) {
			this.bindPopup(this._popup);
		}

		return this;
	},

	update: function () {
		if (this._icon) {
			this._setPos(this._map.latLngToLayerPoint(this._latlng).round());
		}
		return this;
	},

	_initIcon: function () {
		var options = this.options,
		    map = this._map,
		    animation = (map.options.zoomAnimation && map.options.markerZoomAnimation),
		    classToAdd = animation ? 'leaflet-zoom-animated' : 'leaflet-zoom-hide';

		var icon = options.icon.createIcon(this._icon),
			addIcon = false;

		// if we're not reusing the icon, remove the old one and init new one
		if (icon !== this._icon) {
			if (this._icon) {
				this._removeIcon();
			}
			addIcon = true;

			if (options.title) {
				icon.title = options.title;
			}

			if (options.alt) {
				icon.alt = options.alt;
			}
		}

		L.DomUtil.addClass(icon, classToAdd);

		if (options.keyboard) {
			icon.tabIndex = '0';
		}

		this._icon = icon;

		this._initInteraction();

		if (options.riseOnHover) {
			L.DomEvent
				.on(icon, 'mouseover', this._bringToFront, this)
				.on(icon, 'mouseout', this._resetZIndex, this);
		}

		var newShadow = options.icon.createShadow(this._shadow),
			addShadow = false;

		if (newShadow !== this._shadow) {
			this._removeShadow();
			addShadow = true;
		}

		if (newShadow) {
			L.DomUtil.addClass(newShadow, classToAdd);
		}
		this._shadow = newShadow;


		if (options.opacity < 1) {
			this._updateOpacity();
		}


		var panes = this._map._panes;

		if (addIcon) {
			panes.markerPane.appendChild(this._icon);
		}

		if (newShadow && addShadow) {
			panes.shadowPane.appendChild(this._shadow);
		}
	},

	_removeIcon: function () {
		if (this.options.riseOnHover) {
			L.DomEvent
			    .off(this._icon, 'mouseover', this._bringToFront)
			    .off(this._icon, 'mouseout', this._resetZIndex);
		}

		this._map._panes.markerPane.removeChild(this._icon);

		this._icon = null;
	},

	_removeShadow: function () {
		if (this._shadow) {
			this._map._panes.shadowPane.removeChild(this._shadow);
		}
		this._shadow = null;
	},

	_setPos: function (pos) {
		L.DomUtil.setPosition(this._icon, pos);

		if (this._shadow) {
			L.DomUtil.setPosition(this._shadow, pos);
		}

		this._zIndex = pos.y + this.options.zIndexOffset;

		this._resetZIndex();
	},

	_updateZIndex: function (offset) {
		this._icon.style.zIndex = this._zIndex + offset;
	},

	_animateZoom: function (opt) {
		var pos = this._map._latLngToNewLayerPoint(this._latlng, opt.zoom, opt.center).round();

		this._setPos(pos);
	},

	_initInteraction: function () {

		if (!this.options.clickable) { return; }

		// TODO refactor into something shared with Map/Path/etc. to DRY it up

		var icon = this._icon,
		    events = ['dblclick', 'mousedown', 'mouseover', 'mouseout', 'contextmenu'];

		L.DomUtil.addClass(icon, 'leaflet-clickable');
		L.DomEvent.on(icon, 'click', this._onMouseClick, this);
		L.DomEvent.on(icon, 'keypress', this._onKeyPress, this);

		for (var i = 0; i < events.length; i++) {
			L.DomEvent.on(icon, events[i], this._fireMouseEvent, this);
		}

		if (L.Handler.MarkerDrag) {
			this.dragging = new L.Handler.MarkerDrag(this);

			if (this.options.draggable) {
				this.dragging.enable();
			}
		}
	},

	_onMouseClick: function (e) {
		var wasDragged = this.dragging && this.dragging.moved();

		if (this.hasEventListeners(e.type) || wasDragged) {
			L.DomEvent.stopPropagation(e);
		}

		if (wasDragged) { return; }

		if ((!this.dragging || !this.dragging._enabled) && this._map.dragging && this._map.dragging.moved()) { return; }

		this.fire(e.type, {
			originalEvent: e,
			latlng: this._latlng
		});
	},

	_onKeyPress: function (e) {
		if (e.keyCode === 13) {
			this.fire('click', {
				originalEvent: e,
				latlng: this._latlng
			});
		}
	},

	_fireMouseEvent: function (e) {

		this.fire(e.type, {
			originalEvent: e,
			latlng: this._latlng
		});

		// TODO proper custom event propagation
		// this line will always be called if marker is in a FeatureGroup
		if (e.type === 'contextmenu' && this.hasEventListeners(e.type)) {
			L.DomEvent.preventDefault(e);
		}
		if (e.type !== 'mousedown') {
			L.DomEvent.stopPropagation(e);
		} else {
			L.DomEvent.preventDefault(e);
		}
	},

	setOpacity: function (opacity) {
		this.options.opacity = opacity;
		if (this._map) {
			this._updateOpacity();
		}

		return this;
	},

	_updateOpacity: function () {
		L.DomUtil.setOpacity(this._icon, this.options.opacity);
		if (this._shadow) {
			L.DomUtil.setOpacity(this._shadow, this.options.opacity);
		}
	},

	_bringToFront: function () {
		this._updateZIndex(this.options.riseOffset);
	},

	_resetZIndex: function () {
		this._updateZIndex(0);
	}
});

L.marker = function (latlng, options) {
	return new L.Marker(latlng, options);
};


/*
 * L.DivIcon is a lightweight HTML-based icon class (as opposed to the image-based L.Icon)
 * to use with L.Marker.
 */

L.DivIcon = L.Icon.extend({
	options: {
		iconSize: [12, 12], // also can be set through CSS
		/*
		iconAnchor: (Point)
		popupAnchor: (Point)
		html: (String)
		bgPos: (Point)
		*/
		className: 'leaflet-div-icon',
		html: false
	},

	createIcon: function (oldIcon) {
		var div = (oldIcon && oldIcon.tagName === 'DIV') ? oldIcon : document.createElement('div'),
		    options = this.options;

		if (options.html !== false) {
			div.innerHTML = options.html;
		} else {
			div.innerHTML = '';
		}

		if (options.bgPos) {
			div.style.backgroundPosition =
			        (-options.bgPos.x) + 'px ' + (-options.bgPos.y) + 'px';
		}

		this._setIconStyles(div, 'icon');
		return div;
	},

	createShadow: function () {
		return null;
	}
});

L.divIcon = function (options) {
	return new L.DivIcon(options);
};


/*
 * L.Popup is used for displaying popups on the map.
 */

L.Map.mergeOptions({
	closePopupOnClick: true
});

L.Popup = L.Class.extend({
	includes: L.Mixin.Events,

	options: {
		minWidth: 50,
		maxWidth: 300,
		// maxHeight: null,
		autoPan: true,
		closeButton: true,
		offset: [0, 7],
		autoPanPadding: [5, 5],
		// autoPanPaddingTopLeft: null,
		// autoPanPaddingBottomRight: null,
		keepInView: false,
		className: '',
		zoomAnimation: true
	},

	initialize: function (options, source) {
		L.setOptions(this, options);

		this._source = source;
		this._animated = L.Browser.any3d && this.options.zoomAnimation;
		this._isOpen = false;
	},

	onAdd: function (map) {
		this._map = map;

		if (!this._container) {
			this._initLayout();
		}

		var animFade = map.options.fadeAnimation;

		if (animFade) {
			L.DomUtil.setOpacity(this._container, 0);
		}
		map._panes.popupPane.appendChild(this._container);

		map.on(this._getEvents(), this);

		this.update();

		if (animFade) {
			L.DomUtil.setOpacity(this._container, 1);
		}

		this.fire('open');

		map.fire('popupopen', {popup: this});

		if (this._source) {
			this._source.fire('popupopen', {popup: this});
		}
	},

	addTo: function (map) {
		map.addLayer(this);
		return this;
	},

	openOn: function (map) {
		map.openPopup(this);
		return this;
	},

	onRemove: function (map) {
		map._panes.popupPane.removeChild(this._container);

		L.Util.falseFn(this._container.offsetWidth); // force reflow

		map.off(this._getEvents(), this);

		if (map.options.fadeAnimation) {
			L.DomUtil.setOpacity(this._container, 0);
		}

		this._map = null;

		this.fire('close');

		map.fire('popupclose', {popup: this});

		if (this._source) {
			this._source.fire('popupclose', {popup: this});
		}
	},

	getLatLng: function () {
		return this._latlng;
	},

	setLatLng: function (latlng) {
		this._latlng = L.latLng(latlng);
		if (this._map) {
			this._updatePosition();
			this._adjustPan();
		}
		return this;
	},

	getContent: function () {
		return this._content;
	},

	setContent: function (content) {
		this._content = content;
		this.update();
		return this;
	},

	update: function () {
		if (!this._map) { return; }

		this._container.style.visibility = 'hidden';

		this._updateContent();
		this._updateLayout();
		this._updatePosition();

		this._container.style.visibility = '';

		this._adjustPan();
	},

	_getEvents: function () {
		var events = {
			viewreset: this._updatePosition
		};

		if (this._animated) {
			events.zoomanim = this._zoomAnimation;
		}
		if ('closeOnClick' in this.options ? this.options.closeOnClick : this._map.options.closePopupOnClick) {
			events.preclick = this._close;
		}
		if (this.options.keepInView) {
			events.moveend = this._adjustPan;
		}

		return events;
	},

	_close: function () {
		if (this._map) {
			this._map.closePopup(this);
		}
	},

	_initLayout: function () {
		var prefix = 'leaflet-popup',
			containerClass = prefix + ' ' + this.options.className + ' leaflet-zoom-' +
			        (this._animated ? 'animated' : 'hide'),
			container = this._container = L.DomUtil.create('div', containerClass),
			closeButton;

		if (this.options.closeButton) {
			closeButton = this._closeButton =
			        L.DomUtil.create('a', prefix + '-close-button', container);
			closeButton.href = '#close';
			closeButton.innerHTML = '&#215;';
			L.DomEvent.disableClickPropagation(closeButton);

			L.DomEvent.on(closeButton, 'click', this._onCloseButtonClick, this);
		}

		var wrapper = this._wrapper =
		        L.DomUtil.create('div', prefix + '-content-wrapper', container);
		L.DomEvent.disableClickPropagation(wrapper);

		this._contentNode = L.DomUtil.create('div', prefix + '-content', wrapper);

		L.DomEvent.disableScrollPropagation(this._contentNode);
		L.DomEvent.on(wrapper, 'contextmenu', L.DomEvent.stopPropagation);

		this._tipContainer = L.DomUtil.create('div', prefix + '-tip-container', container);
		this._tip = L.DomUtil.create('div', prefix + '-tip', this._tipContainer);
	},

	_updateContent: function () {
		if (!this._content) { return; }

		if (typeof this._content === 'string') {
			this._contentNode.innerHTML = this._content;
		} else {
			while (this._contentNode.hasChildNodes()) {
				this._contentNode.removeChild(this._contentNode.firstChild);
			}
			this._contentNode.appendChild(this._content);
		}
		this.fire('contentupdate');
	},

	_updateLayout: function () {
		var container = this._contentNode,
		    style = container.style;

		style.width = '';
		style.whiteSpace = 'nowrap';

		var width = container.offsetWidth;
		width = Math.min(width, this.options.maxWidth);
		width = Math.max(width, this.options.minWidth);

		style.width = (width + 1) + 'px';
		style.whiteSpace = '';

		style.height = '';

		var height = container.offsetHeight,
		    maxHeight = this.options.maxHeight,
		    scrolledClass = 'leaflet-popup-scrolled';

		if (maxHeight && height > maxHeight) {
			style.height = maxHeight + 'px';
			L.DomUtil.addClass(container, scrolledClass);
		} else {
			L.DomUtil.removeClass(container, scrolledClass);
		}

		this._containerWidth = this._container.offsetWidth;
	},

	_updatePosition: function () {
		if (!this._map) { return; }

		var pos = this._map.latLngToLayerPoint(this._latlng),
		    animated = this._animated,
		    offset = L.point(this.options.offset);

		if (animated) {
			L.DomUtil.setPosition(this._container, pos);
		}

		this._containerBottom = -offset.y - (animated ? 0 : pos.y);
		this._containerLeft = -Math.round(this._containerWidth / 2) + offset.x + (animated ? 0 : pos.x);

		// bottom position the popup in case the height of the popup changes (images loading etc)
		this._container.style.bottom = this._containerBottom + 'px';
		this._container.style.left = this._containerLeft + 'px';
	},

	_zoomAnimation: function (opt) {
		var pos = this._map._latLngToNewLayerPoint(this._latlng, opt.zoom, opt.center);

		L.DomUtil.setPosition(this._container, pos);
	},

	_adjustPan: function () {
		if (!this.options.autoPan) { return; }

		var map = this._map,
		    containerHeight = this._container.offsetHeight,
		    containerWidth = this._containerWidth,

		    layerPos = new L.Point(this._containerLeft, -containerHeight - this._containerBottom);

		if (this._animated) {
			layerPos._add(L.DomUtil.getPosition(this._container));
		}

		var containerPos = map.layerPointToContainerPoint(layerPos),
		    padding = L.point(this.options.autoPanPadding),
		    paddingTL = L.point(this.options.autoPanPaddingTopLeft || padding),
		    paddingBR = L.point(this.options.autoPanPaddingBottomRight || padding),
		    size = map.getSize(),
		    dx = 0,
		    dy = 0;

		if (containerPos.x + containerWidth + paddingBR.x > size.x) { // right
			dx = containerPos.x + containerWidth - size.x + paddingBR.x;
		}
		if (containerPos.x - dx - paddingTL.x < 0) { // left
			dx = containerPos.x - paddingTL.x;
		}
		if (containerPos.y + containerHeight + paddingBR.y > size.y) { // bottom
			dy = containerPos.y + containerHeight - size.y + paddingBR.y;
		}
		if (containerPos.y - dy - paddingTL.y < 0) { // top
			dy = containerPos.y - paddingTL.y;
		}

		if (dx || dy) {
			map
			    .fire('autopanstart')
			    .panBy([dx, dy]);
		}
	},

	_onCloseButtonClick: function (e) {
		this._close();
		L.DomEvent.stop(e);
	}
});

L.popup = function (options, source) {
	return new L.Popup(options, source);
};


L.Map.include({
	openPopup: function (popup, latlng, options) { // (Popup) or (String || HTMLElement, LatLng[, Object])
		this.closePopup();

		if (!(popup instanceof L.Popup)) {
			var content = popup;

			popup = new L.Popup(options)
			    .setLatLng(latlng)
			    .setContent(content);
		}
		popup._isOpen = true;

		this._popup = popup;
		return this.addLayer(popup);
	},

	closePopup: function (popup) {
		if (!popup || popup === this._popup) {
			popup = this._popup;
			this._popup = null;
		}
		if (popup) {
			this.removeLayer(popup);
			popup._isOpen = false;
		}
		return this;
	}
});


/*
 * Popup extension to L.Marker, adding popup-related methods.
 */

L.Marker.include({
	openPopup: function () {
		if (this._popup && this._map && !this._map.hasLayer(this._popup)) {
			this._popup.setLatLng(this._latlng);
			this._map.openPopup(this._popup);
		}

		return this;
	},

	closePopup: function () {
		if (this._popup) {
			this._popup._close();
		}
		return this;
	},

	togglePopup: function () {
		if (this._popup) {
			if (this._popup._isOpen) {
				this.closePopup();
			} else {
				this.openPopup();
			}
		}
		return this;
	},

	bindPopup: function (content, options) {
		var anchor = L.point(this.options.icon.options.popupAnchor || [0, 0]);

		anchor = anchor.add(L.Popup.prototype.options.offset);

		if (options && options.offset) {
			anchor = anchor.add(options.offset);
		}

		options = L.extend({offset: anchor}, options);

		if (!this._popupHandlersAdded) {
			this
			    .on('click', this.togglePopup, this)
			    .on('remove', this.closePopup, this)
			    .on('move', this._movePopup, this);
			this._popupHandlersAdded = true;
		}

		if (content instanceof L.Popup) {
			L.setOptions(content, options);
			this._popup = content;
			content._source = this;
		} else {
			this._popup = new L.Popup(options, this)
				.setContent(content);
		}

		return this;
	},

	setPopupContent: function (content) {
		if (this._popup) {
			this._popup.setContent(content);
		}
		return this;
	},

	unbindPopup: function () {
		if (this._popup) {
			this._popup = null;
			this
			    .off('click', this.togglePopup, this)
			    .off('remove', this.closePopup, this)
			    .off('move', this._movePopup, this);
			this._popupHandlersAdded = false;
		}
		return this;
	},

	getPopup: function () {
		return this._popup;
	},

	_movePopup: function (e) {
		this._popup.setLatLng(e.latlng);
	}
});


/*
 * L.LayerGroup is a class to combine several layers into one so that
 * you can manipulate the group (e.g. add/remove it) as one layer.
 */

L.LayerGroup = L.Class.extend({
	initialize: function (layers) {
		this._layers = {};

		var i, len;

		if (layers) {
			for (i = 0, len = layers.length; i < len; i++) {
				this.addLayer(layers[i]);
			}
		}
	},

	addLayer: function (layer) {
		var id = this.getLayerId(layer);

		this._layers[id] = layer;

		if (this._map) {
			this._map.addLayer(layer);
		}

		return this;
	},

	removeLayer: function (layer) {
		var id = layer in this._layers ? layer : this.getLayerId(layer);

		if (this._map && this._layers[id]) {
			this._map.removeLayer(this._layers[id]);
		}

		delete this._layers[id];

		return this;
	},

	hasLayer: function (layer) {
		if (!layer) { return false; }

		return (layer in this._layers || this.getLayerId(layer) in this._layers);
	},

	clearLayers: function () {
		this.eachLayer(this.removeLayer, this);
		return this;
	},

	invoke: function (methodName) {
		var args = Array.prototype.slice.call(arguments, 1),
		    i, layer;

		for (i in this._layers) {
			layer = this._layers[i];

			if (layer[methodName]) {
				layer[methodName].apply(layer, args);
			}
		}

		return this;
	},

	onAdd: function (map) {
		this._map = map;
		this.eachLayer(map.addLayer, map);
	},

	onRemove: function (map) {
		this.eachLayer(map.removeLayer, map);
		this._map = null;
	},

	addTo: function (map) {
		map.addLayer(this);
		return this;
	},

	eachLayer: function (method, context) {
		for (var i in this._layers) {
			method.call(context, this._layers[i]);
		}
		return this;
	},

	getLayer: function (id) {
		return this._layers[id];
	},

	getLayers: function () {
		var layers = [];

		for (var i in this._layers) {
			layers.push(this._layers[i]);
		}
		return layers;
	},

	setZIndex: function (zIndex) {
		return this.invoke('setZIndex', zIndex);
	},

	getLayerId: function (layer) {
		return L.stamp(layer);
	}
});

L.layerGroup = function (layers) {
	return new L.LayerGroup(layers);
};


/*
 * L.FeatureGroup extends L.LayerGroup by introducing mouse events and additional methods
 * shared between a group of interactive layers (like vectors or markers).
 */

L.FeatureGroup = L.LayerGroup.extend({
	includes: L.Mixin.Events,

	statics: {
		EVENTS: 'click dblclick mouseover mouseout mousemove contextmenu popupopen popupclose'
	},

	addLayer: function (layer) {
		if (this.hasLayer(layer)) {
			return this;
		}

		if ('on' in layer) {
			layer.on(L.FeatureGroup.EVENTS, this._propagateEvent, this);
		}

		L.LayerGroup.prototype.addLayer.call(this, layer);

		if (this._popupContent && layer.bindPopup) {
			layer.bindPopup(this._popupContent, this._popupOptions);
		}

		return this.fire('layeradd', {layer: layer});
	},

	removeLayer: function (layer) {
		if (!this.hasLayer(layer)) {
			return this;
		}
		if (layer in this._layers) {
			layer = this._layers[layer];
		}

		if ('off' in layer) {
			layer.off(L.FeatureGroup.EVENTS, this._propagateEvent, this);
		}

		L.LayerGroup.prototype.removeLayer.call(this, layer);

		if (this._popupContent) {
			this.invoke('unbindPopup');
		}

		return this.fire('layerremove', {layer: layer});
	},

	bindPopup: function (content, options) {
		this._popupContent = content;
		this._popupOptions = options;
		return this.invoke('bindPopup', content, options);
	},

	openPopup: function (latlng) {
		// open popup on the first layer
		for (var id in this._layers) {
			this._layers[id].openPopup(latlng);
			break;
		}
		return this;
	},

	setStyle: function (style) {
		return this.invoke('setStyle', style);
	},

	bringToFront: function () {
		return this.invoke('bringToFront');
	},

	bringToBack: function () {
		return this.invoke('bringToBack');
	},

	getBounds: function () {
		var bounds = new L.LatLngBounds();

		this.eachLayer(function (layer) {
			bounds.extend(layer instanceof L.Marker ? layer.getLatLng() : layer.getBounds());
		});

		return bounds;
	},

	_propagateEvent: function (e) {
		e = L.extend({
			layer: e.target,
			target: this
		}, e);
		this.fire(e.type, e);
	}
});

L.featureGroup = function (layers) {
	return new L.FeatureGroup(layers);
};


/*
 * L.Path is a base class for rendering vector paths on a map. Inherited by Polyline, Circle, etc.
 */

L.Path = L.Class.extend({
	includes: [L.Mixin.Events],

	statics: {
		// how much to extend the clip area around the map view
		// (relative to its size, e.g. 0.5 is half the screen in each direction)
		// set it so that SVG element doesn't exceed 1280px (vectors flicker on dragend if it is)
		CLIP_PADDING: (function () {
			var max = L.Browser.mobile ? 1280 : 2000,
			    target = (max / Math.max(window.outerWidth, window.outerHeight) - 1) / 2;
			return Math.max(0, Math.min(0.5, target));
		})()
	},

	options: {
		stroke: true,
		color: '#0033ff',
		dashArray: null,
		lineCap: null,
		lineJoin: null,
		weight: 5,
		opacity: 0.5,

		fill: false,
		fillColor: null, //same as color by default
		fillOpacity: 0.2,

		clickable: true
	},

	initialize: function (options) {
		L.setOptions(this, options);
	},

	onAdd: function (map) {
		this._map = map;

		if (!this._container) {
			this._initElements();
			this._initEvents();
		}

		this.projectLatlngs();
		this._updatePath();

		if (this._container) {
			this._map._pathRoot.appendChild(this._container);
		}

		this.fire('add');

		map.on({
			'viewreset': this.projectLatlngs,
			'moveend': this._updatePath
		}, this);
	},

	addTo: function (map) {
		map.addLayer(this);
		return this;
	},

	onRemove: function (map) {
		map._pathRoot.removeChild(this._container);

		// Need to fire remove event before we set _map to null as the event hooks might need the object
		this.fire('remove');
		this._map = null;

		if (L.Browser.vml) {
			this._container = null;
			this._stroke = null;
			this._fill = null;
		}

		map.off({
			'viewreset': this.projectLatlngs,
			'moveend': this._updatePath
		}, this);
	},

	projectLatlngs: function () {
		// do all projection stuff here
	},

	setStyle: function (style) {
		L.setOptions(this, style);

		if (this._container) {
			this._updateStyle();
		}

		return this;
	},

	redraw: function () {
		if (this._map) {
			this.projectLatlngs();
			this._updatePath();
		}
		return this;
	}
});

L.Map.include({
	_updatePathViewport: function () {
		var p = L.Path.CLIP_PADDING,
		    size = this.getSize(),
		    panePos = L.DomUtil.getPosition(this._mapPane),
		    min = panePos.multiplyBy(-1)._subtract(size.multiplyBy(p)._round()),
		    max = min.add(size.multiplyBy(1 + p * 2)._round());

		this._pathViewport = new L.Bounds(min, max);
	}
});


/*
 * Extends L.Path with SVG-specific rendering code.
 */

L.Path.SVG_NS = 'http://www.w3.org/2000/svg';

L.Browser.svg = !!(document.createElementNS && document.createElementNS(L.Path.SVG_NS, 'svg').createSVGRect);

L.Path = L.Path.extend({
	statics: {
		SVG: L.Browser.svg
	},

	bringToFront: function () {
		var root = this._map._pathRoot,
		    path = this._container;

		if (path && root.lastChild !== path) {
			root.appendChild(path);
		}
		return this;
	},

	bringToBack: function () {
		var root = this._map._pathRoot,
		    path = this._container,
		    first = root.firstChild;

		if (path && first !== path) {
			root.insertBefore(path, first);
		}
		return this;
	},

	getPathString: function () {
		// form path string here
	},

	_createElement: function (name) {
		return document.createElementNS(L.Path.SVG_NS, name);
	},

	_initElements: function () {
		this._map._initPathRoot();
		this._initPath();
		this._initStyle();
	},

	_initPath: function () {
		this._container = this._createElement('g');

		this._path = this._createElement('path');

		if (this.options.className) {
			L.DomUtil.addClass(this._path, this.options.className);
		}

		this._container.appendChild(this._path);
	},

	_initStyle: function () {
		if (this.options.stroke) {
			this._path.setAttribute('stroke-linejoin', 'round');
			this._path.setAttribute('stroke-linecap', 'round');
		}
		if (this.options.fill) {
			this._path.setAttribute('fill-rule', 'evenodd');
		}
		if (this.options.pointerEvents) {
			this._path.setAttribute('pointer-events', this.options.pointerEvents);
		}
		if (!this.options.clickable && !this.options.pointerEvents) {
			this._path.setAttribute('pointer-events', 'none');
		}
		this._updateStyle();
	},

	_updateStyle: function () {
		if (this.options.stroke) {
			this._path.setAttribute('stroke', this.options.color);
			this._path.setAttribute('stroke-opacity', this.options.opacity);
			this._path.setAttribute('stroke-width', this.options.weight);
			if (this.options.dashArray) {
				this._path.setAttribute('stroke-dasharray', this.options.dashArray);
			} else {
				this._path.removeAttribute('stroke-dasharray');
			}
			if (this.options.lineCap) {
				this._path.setAttribute('stroke-linecap', this.options.lineCap);
			}
			if (this.options.lineJoin) {
				this._path.setAttribute('stroke-linejoin', this.options.lineJoin);
			}
		} else {
			this._path.setAttribute('stroke', 'none');
		}
		if (this.options.fill) {
			this._path.setAttribute('fill', this.options.fillColor || this.options.color);
			this._path.setAttribute('fill-opacity', this.options.fillOpacity);
		} else {
			this._path.setAttribute('fill', 'none');
		}
	},

	_updatePath: function () {
		var str = this.getPathString();
		if (!str) {
			// fix webkit empty string parsing bug
			str = 'M0 0';
		}
		this._path.setAttribute('d', str);
	},

	// TODO remove duplication with L.Map
	_initEvents: function () {
		if (this.options.clickable) {
			if (L.Browser.svg || !L.Browser.vml) {
				L.DomUtil.addClass(this._path, 'leaflet-clickable');
			}

			L.DomEvent.on(this._container, 'click', this._onMouseClick, this);

			var events = ['dblclick', 'mousedown', 'mouseover',
			              'mouseout', 'mousemove', 'contextmenu'];
			for (var i = 0; i < events.length; i++) {
				L.DomEvent.on(this._container, events[i], this._fireMouseEvent, this);
			}
		}
	},

	_onMouseClick: function (e) {
		if (this._map.dragging && this._map.dragging.moved()) { return; }

		this._fireMouseEvent(e);
	},

	_fireMouseEvent: function (e) {
		if (!this._map || !this.hasEventListeners(e.type)) { return; }

		var map = this._map,
		    containerPoint = map.mouseEventToContainerPoint(e),
		    layerPoint = map.containerPointToLayerPoint(containerPoint),
		    latlng = map.layerPointToLatLng(layerPoint);

		this.fire(e.type, {
			latlng: latlng,
			layerPoint: layerPoint,
			containerPoint: containerPoint,
			originalEvent: e
		});

		if (e.type === 'contextmenu') {
			L.DomEvent.preventDefault(e);
		}
		if (e.type !== 'mousemove') {
			L.DomEvent.stopPropagation(e);
		}
	}
});

L.Map.include({
	_initPathRoot: function () {
		if (!this._pathRoot) {
			this._pathRoot = L.Path.prototype._createElement('svg');
			this._panes.overlayPane.appendChild(this._pathRoot);

			if (this.options.zoomAnimation && L.Browser.any3d) {
				L.DomUtil.addClass(this._pathRoot, 'leaflet-zoom-animated');

				this.on({
					'zoomanim': this._animatePathZoom,
					'zoomend': this._endPathZoom
				});
			} else {
				L.DomUtil.addClass(this._pathRoot, 'leaflet-zoom-hide');
			}

			this.on('moveend', this._updateSvgViewport);
			this._updateSvgViewport();
		}
	},

	_animatePathZoom: function (e) {
		var scale = this.getZoomScale(e.zoom),
		    offset = this._getCenterOffset(e.center)._multiplyBy(-scale)._add(this._pathViewport.min);

		this._pathRoot.style[L.DomUtil.TRANSFORM] =
		        L.DomUtil.getTranslateString(offset) + ' scale(' + scale + ') ';

		this._pathZooming = true;
	},

	_endPathZoom: function () {
		this._pathZooming = false;
	},

	_updateSvgViewport: function () {

		if (this._pathZooming) {
			// Do not update SVGs while a zoom animation is going on otherwise the animation will break.
			// When the zoom animation ends we will be updated again anyway
			// This fixes the case where you do a momentum move and zoom while the move is still ongoing.
			return;
		}

		this._updatePathViewport();

		var vp = this._pathViewport,
		    min = vp.min,
		    max = vp.max,
		    width = max.x - min.x,
		    height = max.y - min.y,
		    root = this._pathRoot,
		    pane = this._panes.overlayPane;

		// Hack to make flicker on drag end on mobile webkit less irritating
		if (L.Browser.mobileWebkit) {
			pane.removeChild(root);
		}

		L.DomUtil.setPosition(root, min);
		root.setAttribute('width', width);
		root.setAttribute('height', height);
		root.setAttribute('viewBox', [min.x, min.y, width, height].join(' '));

		if (L.Browser.mobileWebkit) {
			pane.appendChild(root);
		}
	}
});


/*
 * Popup extension to L.Path (polylines, polygons, circles), adding popup-related methods.
 */

L.Path.include({

	bindPopup: function (content, options) {

		if (content instanceof L.Popup) {
			this._popup = content;
		} else {
			if (!this._popup || options) {
				this._popup = new L.Popup(options, this);
			}
			this._popup.setContent(content);
		}

		if (!this._popupHandlersAdded) {
			this
			    .on('click', this._openPopup, this)
			    .on('remove', this.closePopup, this);

			this._popupHandlersAdded = true;
		}

		return this;
	},

	unbindPopup: function () {
		if (this._popup) {
			this._popup = null;
			this
			    .off('click', this._openPopup)
			    .off('remove', this.closePopup);

			this._popupHandlersAdded = false;
		}
		return this;
	},

	openPopup: function (latlng) {

		if (this._popup) {
			// open the popup from one of the path's points if not specified
			latlng = latlng || this._latlng ||
			         this._latlngs[Math.floor(this._latlngs.length / 2)];

			this._openPopup({latlng: latlng});
		}

		return this;
	},

	closePopup: function () {
		if (this._popup) {
			this._popup._close();
		}
		return this;
	},

	_openPopup: function (e) {
		this._popup.setLatLng(e.latlng);
		this._map.openPopup(this._popup);
	}
});


/*
 * Vector rendering for IE6-8 through VML.
 * Thanks to Dmitry Baranovsky and his Raphael library for inspiration!
 */

L.Browser.vml = !L.Browser.svg && (function () {
	try {
		var div = document.createElement('div');
		div.innerHTML = '<v:shape adj="1"/>';

		var shape = div.firstChild;
		shape.style.behavior = 'url(#default#VML)';

		return shape && (typeof shape.adj === 'object');

	} catch (e) {
		return false;
	}
}());

L.Path = L.Browser.svg || !L.Browser.vml ? L.Path : L.Path.extend({
	statics: {
		VML: true,
		CLIP_PADDING: 0.02
	},

	_createElement: (function () {
		try {
			document.namespaces.add('lvml', 'urn:schemas-microsoft-com:vml');
			return function (name) {
				return document.createElement('<lvml:' + name + ' class="lvml">');
			};
		} catch (e) {
			return function (name) {
				return document.createElement(
				        '<' + name + ' xmlns="urn:schemas-microsoft.com:vml" class="lvml">');
			};
		}
	}()),

	_initPath: function () {
		var container = this._container = this._createElement('shape');

		L.DomUtil.addClass(container, 'leaflet-vml-shape' +
			(this.options.className ? ' ' + this.options.className : ''));

		if (this.options.clickable) {
			L.DomUtil.addClass(container, 'leaflet-clickable');
		}

		container.coordsize = '1 1';

		this._path = this._createElement('path');
		container.appendChild(this._path);

		this._map._pathRoot.appendChild(container);
	},

	_initStyle: function () {
		this._updateStyle();
	},

	_updateStyle: function () {
		var stroke = this._stroke,
		    fill = this._fill,
		    options = this.options,
		    container = this._container;

		container.stroked = options.stroke;
		container.filled = options.fill;

		if (options.stroke) {
			if (!stroke) {
				stroke = this._stroke = this._createElement('stroke');
				stroke.endcap = 'round';
				container.appendChild(stroke);
			}
			stroke.weight = options.weight + 'px';
			stroke.color = options.color;
			stroke.opacity = options.opacity;

			if (options.dashArray) {
				stroke.dashStyle = L.Util.isArray(options.dashArray) ?
				    options.dashArray.join(' ') :
				    options.dashArray.replace(/( *, *)/g, ' ');
			} else {
				stroke.dashStyle = '';
			}
			if (options.lineCap) {
				stroke.endcap = options.lineCap.replace('butt', 'flat');
			}
			if (options.lineJoin) {
				stroke.joinstyle = options.lineJoin;
			}

		} else if (stroke) {
			container.removeChild(stroke);
			this._stroke = null;
		}

		if (options.fill) {
			if (!fill) {
				fill = this._fill = this._createElement('fill');
				container.appendChild(fill);
			}
			fill.color = options.fillColor || options.color;
			fill.opacity = options.fillOpacity;

		} else if (fill) {
			container.removeChild(fill);
			this._fill = null;
		}
	},

	_updatePath: function () {
		var style = this._container.style;

		style.display = 'none';
		this._path.v = this.getPathString() + ' '; // the space fixes IE empty path string bug
		style.display = '';
	}
});

L.Map.include(L.Browser.svg || !L.Browser.vml ? {} : {
	_initPathRoot: function () {
		if (this._pathRoot) { return; }

		var root = this._pathRoot = document.createElement('div');
		root.className = 'leaflet-vml-container';
		this._panes.overlayPane.appendChild(root);

		this.on('moveend', this._updatePathViewport);
		this._updatePathViewport();
	}
});


/*
 * Vector rendering for all browsers that support canvas.
 */

L.Browser.canvas = (function () {
	return !!document.createElement('canvas').getContext;
}());

L.Path = (L.Path.SVG && !window.L_PREFER_CANVAS) || !L.Browser.canvas ? L.Path : L.Path.extend({
	statics: {
		//CLIP_PADDING: 0.02, // not sure if there's a need to set it to a small value
		CANVAS: true,
		SVG: false
	},

	redraw: function () {
		if (this._map) {
			this.projectLatlngs();
			this._requestUpdate();
		}
		return this;
	},

	setStyle: function (style) {
		L.setOptions(this, style);

		if (this._map) {
			this._updateStyle();
			this._requestUpdate();
		}
		return this;
	},

	onRemove: function (map) {
		map
		    .off('viewreset', this.projectLatlngs, this)
		    .off('moveend', this._updatePath, this);

		if (this.options.clickable) {
			this._map.off('click', this._onClick, this);
			this._map.off('mousemove', this._onMouseMove, this);
		}

		this._requestUpdate();
		
		this.fire('remove');
		this._map = null;
	},

	_requestUpdate: function () {
		if (this._map && !L.Path._updateRequest) {
			L.Path._updateRequest = L.Util.requestAnimFrame(this._fireMapMoveEnd, this._map);
		}
	},

	_fireMapMoveEnd: function () {
		L.Path._updateRequest = null;
		this.fire('moveend');
	},

	_initElements: function () {
		this._map._initPathRoot();
		this._ctx = this._map._canvasCtx;
	},

	_updateStyle: function () {
		var options = this.options;

		if (options.stroke) {
			this._ctx.lineWidth = options.weight;
			this._ctx.strokeStyle = options.color;
		}
		if (options.fill) {
			this._ctx.fillStyle = options.fillColor || options.color;
		}

		if (options.lineCap) {
			this._ctx.lineCap = options.lineCap;
		}
		if (options.lineJoin) {
			this._ctx.lineJoin = options.lineJoin;
		}
	},

	_drawPath: function () {
		var i, j, len, len2, point, drawMethod;

		this._ctx.beginPath();

		for (i = 0, len = this._parts.length; i < len; i++) {
			for (j = 0, len2 = this._parts[i].length; j < len2; j++) {
				point = this._parts[i][j];
				drawMethod = (j === 0 ? 'move' : 'line') + 'To';

				this._ctx[drawMethod](point.x, point.y);
			}
			// TODO refactor ugly hack
			if (this instanceof L.Polygon) {
				this._ctx.closePath();
			}
		}
	},

	_checkIfEmpty: function () {
		return !this._parts.length;
	},

	_updatePath: function () {
		if (this._checkIfEmpty()) { return; }

		var ctx = this._ctx,
		    options = this.options;

		this._drawPath();
		ctx.save();
		this._updateStyle();

		if (options.fill) {
			ctx.globalAlpha = options.fillOpacity;
			ctx.fill(options.fillRule || 'evenodd');
		}

		if (options.stroke) {
			ctx.globalAlpha = options.opacity;
			ctx.stroke();
		}

		ctx.restore();

		// TODO optimization: 1 fill/stroke for all features with equal style instead of 1 for each feature
	},

	_initEvents: function () {
		if (this.options.clickable) {
			this._map.on('mousemove', this._onMouseMove, this);
			this._map.on('click dblclick contextmenu', this._fireMouseEvent, this);
		}
	},

	_fireMouseEvent: function (e) {
		if (this._containsPoint(e.layerPoint)) {
			this.fire(e.type, e);
		}
	},

	_onMouseMove: function (e) {
		if (!this._map || this._map._animatingZoom) { return; }

		// TODO don't do on each move
		if (this._containsPoint(e.layerPoint)) {
			this._ctx.canvas.style.cursor = 'pointer';
			this._mouseInside = true;
			this.fire('mouseover', e);

		} else if (this._mouseInside) {
			this._ctx.canvas.style.cursor = '';
			this._mouseInside = false;
			this.fire('mouseout', e);
		}
	}
});

L.Map.include((L.Path.SVG && !window.L_PREFER_CANVAS) || !L.Browser.canvas ? {} : {
	_initPathRoot: function () {
		var root = this._pathRoot,
		    ctx;

		if (!root) {
			root = this._pathRoot = document.createElement('canvas');
			root.style.position = 'absolute';
			ctx = this._canvasCtx = root.getContext('2d');

			ctx.lineCap = 'round';
			ctx.lineJoin = 'round';

			this._panes.overlayPane.appendChild(root);

			if (this.options.zoomAnimation) {
				this._pathRoot.className = 'leaflet-zoom-animated';
				this.on('zoomanim', this._animatePathZoom);
				this.on('zoomend', this._endPathZoom);
			}
			this.on('moveend', this._updateCanvasViewport);
			this._updateCanvasViewport();
		}
	},

	_updateCanvasViewport: function () {
		// don't redraw while zooming. See _updateSvgViewport for more details
		if (this._pathZooming) { return; }
		this._updatePathViewport();

		var vp = this._pathViewport,
		    min = vp.min,
		    size = vp.max.subtract(min),
		    root = this._pathRoot;

		//TODO check if this works properly on mobile webkit
		L.DomUtil.setPosition(root, min);
		root.width = size.x;
		root.height = size.y;
		root.getContext('2d').translate(-min.x, -min.y);
	}
});


/*
 * L.LineUtil contains different utility functions for line segments
 * and polylines (clipping, simplification, distances, etc.)
 */

/*jshint bitwise:false */ // allow bitwise operations for this file

L.LineUtil = {

	// Simplify polyline with vertex reduction and Douglas-Peucker simplification.
	// Improves rendering performance dramatically by lessening the number of points to draw.

	simplify: function (/*Point[]*/ points, /*Number*/ tolerance) {
		if (!tolerance || !points.length) {
			return points.slice();
		}

		var sqTolerance = tolerance * tolerance;

		// stage 1: vertex reduction
		points = this._reducePoints(points, sqTolerance);

		// stage 2: Douglas-Peucker simplification
		points = this._simplifyDP(points, sqTolerance);

		return points;
	},

	// distance from a point to a segment between two points
	pointToSegmentDistance:  function (/*Point*/ p, /*Point*/ p1, /*Point*/ p2) {
		return Math.sqrt(this._sqClosestPointOnSegment(p, p1, p2, true));
	},

	closestPointOnSegment: function (/*Point*/ p, /*Point*/ p1, /*Point*/ p2) {
		return this._sqClosestPointOnSegment(p, p1, p2);
	},

	// Douglas-Peucker simplification, see http://en.wikipedia.org/wiki/Douglas-Peucker_algorithm
	_simplifyDP: function (points, sqTolerance) {

		var len = points.length,
		    ArrayConstructor = typeof Uint8Array !== undefined + '' ? Uint8Array : Array,
		    markers = new ArrayConstructor(len);

		markers[0] = markers[len - 1] = 1;

		this._simplifyDPStep(points, markers, sqTolerance, 0, len - 1);

		var i,
		    newPoints = [];

		for (i = 0; i < len; i++) {
			if (markers[i]) {
				newPoints.push(points[i]);
			}
		}

		return newPoints;
	},

	_simplifyDPStep: function (points, markers, sqTolerance, first, last) {

		var maxSqDist = 0,
		    index, i, sqDist;

		for (i = first + 1; i <= last - 1; i++) {
			sqDist = this._sqClosestPointOnSegment(points[i], points[first], points[last], true);

			if (sqDist > maxSqDist) {
				index = i;
				maxSqDist = sqDist;
			}
		}

		if (maxSqDist > sqTolerance) {
			markers[index] = 1;

			this._simplifyDPStep(points, markers, sqTolerance, first, index);
			this._simplifyDPStep(points, markers, sqTolerance, index, last);
		}
	},

	// reduce points that are too close to each other to a single point
	_reducePoints: function (points, sqTolerance) {
		var reducedPoints = [points[0]];

		for (var i = 1, prev = 0, len = points.length; i < len; i++) {
			if (this._sqDist(points[i], points[prev]) > sqTolerance) {
				reducedPoints.push(points[i]);
				prev = i;
			}
		}
		if (prev < len - 1) {
			reducedPoints.push(points[len - 1]);
		}
		return reducedPoints;
	},

	// Cohen-Sutherland line clipping algorithm.
	// Used to avoid rendering parts of a polyline that are not currently visible.

	clipSegment: function (a, b, bounds, useLastCode) {
		var codeA = useLastCode ? this._lastCode : this._getBitCode(a, bounds),
		    codeB = this._getBitCode(b, bounds),

		    codeOut, p, newCode;

		// save 2nd code to avoid calculating it on the next segment
		this._lastCode = codeB;

		while (true) {
			// if a,b is inside the clip window (trivial accept)
			if (!(codeA | codeB)) {
				return [a, b];
			// if a,b is outside the clip window (trivial reject)
			} else if (codeA & codeB) {
				return false;
			// other cases
			} else {
				codeOut = codeA || codeB;
				p = this._getEdgeIntersection(a, b, codeOut, bounds);
				newCode = this._getBitCode(p, bounds);

				if (codeOut === codeA) {
					a = p;
					codeA = newCode;
				} else {
					b = p;
					codeB = newCode;
				}
			}
		}
	},

	_getEdgeIntersection: function (a, b, code, bounds) {
		var dx = b.x - a.x,
		    dy = b.y - a.y,
		    min = bounds.min,
		    max = bounds.max;

		if (code & 8) { // top
			return new L.Point(a.x + dx * (max.y - a.y) / dy, max.y);
		} else if (code & 4) { // bottom
			return new L.Point(a.x + dx * (min.y - a.y) / dy, min.y);
		} else if (code & 2) { // right
			return new L.Point(max.x, a.y + dy * (max.x - a.x) / dx);
		} else if (code & 1) { // left
			return new L.Point(min.x, a.y + dy * (min.x - a.x) / dx);
		}
	},

	_getBitCode: function (/*Point*/ p, bounds) {
		var code = 0;

		if (p.x < bounds.min.x) { // left
			code |= 1;
		} else if (p.x > bounds.max.x) { // right
			code |= 2;
		}
		if (p.y < bounds.min.y) { // bottom
			code |= 4;
		} else if (p.y > bounds.max.y) { // top
			code |= 8;
		}

		return code;
	},

	// square distance (to avoid unnecessary Math.sqrt calls)
	_sqDist: function (p1, p2) {
		var dx = p2.x - p1.x,
		    dy = p2.y - p1.y;
		return dx * dx + dy * dy;
	},

	// return closest point on segment or distance to that point
	_sqClosestPointOnSegment: function (p, p1, p2, sqDist) {
		var x = p1.x,
		    y = p1.y,
		    dx = p2.x - x,
		    dy = p2.y - y,
		    dot = dx * dx + dy * dy,
		    t;

		if (dot > 0) {
			t = ((p.x - x) * dx + (p.y - y) * dy) / dot;

			if (t > 1) {
				x = p2.x;
				y = p2.y;
			} else if (t > 0) {
				x += dx * t;
				y += dy * t;
			}
		}

		dx = p.x - x;
		dy = p.y - y;

		return sqDist ? dx * dx + dy * dy : new L.Point(x, y);
	}
};


/*
 * L.Polyline is used to display polylines on a map.
 */

L.Polyline = L.Path.extend({
	initialize: function (latlngs, options) {
		L.Path.prototype.initialize.call(this, options);

		this._latlngs = this._convertLatLngs(latlngs);
	},

	options: {
		// how much to simplify the polyline on each zoom level
		// more = better performance and smoother look, less = more accurate
		smoothFactor: 1.0,
		noClip: false
	},

	projectLatlngs: function () {
		this._originalPoints = [];

		for (var i = 0, len = this._latlngs.length; i < len; i++) {
			this._originalPoints[i] = this._map.latLngToLayerPoint(this._latlngs[i]);
		}
	},

	getPathString: function () {
		for (var i = 0, len = this._parts.length, str = ''; i < len; i++) {
			str += this._getPathPartStr(this._parts[i]);
		}
		return str;
	},

	getLatLngs: function () {
		return this._latlngs;
	},

	setLatLngs: function (latlngs) {
		this._latlngs = this._convertLatLngs(latlngs);
		return this.redraw();
	},

	addLatLng: function (latlng) {
		this._latlngs.push(L.latLng(latlng));
		return this.redraw();
	},

	spliceLatLngs: function () { // (Number index, Number howMany)
		var removed = [].splice.apply(this._latlngs, arguments);
		this._convertLatLngs(this._latlngs, true);
		this.redraw();
		return removed;
	},

	closestLayerPoint: function (p) {
		var minDistance = Infinity, parts = this._parts, p1, p2, minPoint = null;

		for (var j = 0, jLen = parts.length; j < jLen; j++) {
			var points = parts[j];
			for (var i = 1, len = points.length; i < len; i++) {
				p1 = points[i - 1];
				p2 = points[i];
				var sqDist = L.LineUtil._sqClosestPointOnSegment(p, p1, p2, true);
				if (sqDist < minDistance) {
					minDistance = sqDist;
					minPoint = L.LineUtil._sqClosestPointOnSegment(p, p1, p2);
				}
			}
		}
		if (minPoint) {
			minPoint.distance = Math.sqrt(minDistance);
		}
		return minPoint;
	},

	getBounds: function () {
		return new L.LatLngBounds(this.getLatLngs());
	},

	_convertLatLngs: function (latlngs, overwrite) {
		var i, len, target = overwrite ? latlngs : [];

		for (i = 0, len = latlngs.length; i < len; i++) {
			if (L.Util.isArray(latlngs[i]) && typeof latlngs[i][0] !== 'number') {
				return;
			}
			target[i] = L.latLng(latlngs[i]);
		}
		return target;
	},

	_initEvents: function () {
		L.Path.prototype._initEvents.call(this);
	},

	_getPathPartStr: function (points) {
		var round = L.Path.VML;

		for (var j = 0, len2 = points.length, str = '', p; j < len2; j++) {
			p = points[j];
			if (round) {
				p._round();
			}
			str += (j ? 'L' : 'M') + p.x + ' ' + p.y;
		}
		return str;
	},

	_clipPoints: function () {
		var points = this._originalPoints,
		    len = points.length,
		    i, k, segment;

		if (this.options.noClip) {
			this._parts = [points];
			return;
		}

		this._parts = [];

		var parts = this._parts,
		    vp = this._map._pathViewport,
		    lu = L.LineUtil;

		for (i = 0, k = 0; i < len - 1; i++) {
			segment = lu.clipSegment(points[i], points[i + 1], vp, i);
			if (!segment) {
				continue;
			}

			parts[k] = parts[k] || [];
			parts[k].push(segment[0]);

			// if segment goes out of screen, or it's the last one, it's the end of the line part
			if ((segment[1] !== points[i + 1]) || (i === len - 2)) {
				parts[k].push(segment[1]);
				k++;
			}
		}
	},

	// simplify each clipped part of the polyline
	_simplifyPoints: function () {
		var parts = this._parts,
		    lu = L.LineUtil;

		for (var i = 0, len = parts.length; i < len; i++) {
			parts[i] = lu.simplify(parts[i], this.options.smoothFactor);
		}
	},

	_updatePath: function () {
		if (!this._map) { return; }

		this._clipPoints();
		this._simplifyPoints();

		L.Path.prototype._updatePath.call(this);
	}
});

L.polyline = function (latlngs, options) {
	return new L.Polyline(latlngs, options);
};


/*
 * L.PolyUtil contains utility functions for polygons (clipping, etc.).
 */

/*jshint bitwise:false */ // allow bitwise operations here

L.PolyUtil = {};

/*
 * Sutherland-Hodgeman polygon clipping algorithm.
 * Used to avoid rendering parts of a polygon that are not currently visible.
 */
L.PolyUtil.clipPolygon = function (points, bounds) {
	var clippedPoints,
	    edges = [1, 4, 2, 8],
	    i, j, k,
	    a, b,
	    len, edge, p,
	    lu = L.LineUtil;

	for (i = 0, len = points.length; i < len; i++) {
		points[i]._code = lu._getBitCode(points[i], bounds);
	}

	// for each edge (left, bottom, right, top)
	for (k = 0; k < 4; k++) {
		edge = edges[k];
		clippedPoints = [];

		for (i = 0, len = points.length, j = len - 1; i < len; j = i++) {
			a = points[i];
			b = points[j];

			// if a is inside the clip window
			if (!(a._code & edge)) {
				// if b is outside the clip window (a->b goes out of screen)
				if (b._code & edge) {
					p = lu._getEdgeIntersection(b, a, edge, bounds);
					p._code = lu._getBitCode(p, bounds);
					clippedPoints.push(p);
				}
				clippedPoints.push(a);

			// else if b is inside the clip window (a->b enters the screen)
			} else if (!(b._code & edge)) {
				p = lu._getEdgeIntersection(b, a, edge, bounds);
				p._code = lu._getBitCode(p, bounds);
				clippedPoints.push(p);
			}
		}
		points = clippedPoints;
	}

	return points;
};


/*
 * L.Polygon is used to display polygons on a map.
 */

L.Polygon = L.Polyline.extend({
	options: {
		fill: true
	},

	initialize: function (latlngs, options) {
		L.Polyline.prototype.initialize.call(this, latlngs, options);
		this._initWithHoles(latlngs);
	},

	_initWithHoles: function (latlngs) {
		var i, len, hole;
		if (latlngs && L.Util.isArray(latlngs[0]) && (typeof latlngs[0][0] !== 'number')) {
			this._latlngs = this._convertLatLngs(latlngs[0]);
			this._holes = latlngs.slice(1);

			for (i = 0, len = this._holes.length; i < len; i++) {
				hole = this._holes[i] = this._convertLatLngs(this._holes[i]);
				if (hole[0].equals(hole[hole.length - 1])) {
					hole.pop();
				}
			}
		}

		// filter out last point if its equal to the first one
		latlngs = this._latlngs;

		if (latlngs.length >= 2 && latlngs[0].equals(latlngs[latlngs.length - 1])) {
			latlngs.pop();
		}
	},

	projectLatlngs: function () {
		L.Polyline.prototype.projectLatlngs.call(this);

		// project polygon holes points
		// TODO move this logic to Polyline to get rid of duplication
		this._holePoints = [];

		if (!this._holes) { return; }

		var i, j, len, len2;

		for (i = 0, len = this._holes.length; i < len; i++) {
			this._holePoints[i] = [];

			for (j = 0, len2 = this._holes[i].length; j < len2; j++) {
				this._holePoints[i][j] = this._map.latLngToLayerPoint(this._holes[i][j]);
			}
		}
	},

	setLatLngs: function (latlngs) {
		if (latlngs && L.Util.isArray(latlngs[0]) && (typeof latlngs[0][0] !== 'number')) {
			this._initWithHoles(latlngs);
			return this.redraw();
		} else {
			return L.Polyline.prototype.setLatLngs.call(this, latlngs);
		}
	},

	_clipPoints: function () {
		var points = this._originalPoints,
		    newParts = [];

		this._parts = [points].concat(this._holePoints);

		if (this.options.noClip) { return; }

		for (var i = 0, len = this._parts.length; i < len; i++) {
			var clipped = L.PolyUtil.clipPolygon(this._parts[i], this._map._pathViewport);
			if (clipped.length) {
				newParts.push(clipped);
			}
		}

		this._parts = newParts;
	},

	_getPathPartStr: function (points) {
		var str = L.Polyline.prototype._getPathPartStr.call(this, points);
		return str + (L.Browser.svg ? 'z' : 'x');
	}
});

L.polygon = function (latlngs, options) {
	return new L.Polygon(latlngs, options);
};


/*
 * Contains L.MultiPolyline and L.MultiPolygon layers.
 */

(function () {
	function createMulti(Klass) {

		return L.FeatureGroup.extend({

			initialize: function (latlngs, options) {
				this._layers = {};
				this._options = options;
				this.setLatLngs(latlngs);
			},

			setLatLngs: function (latlngs) {
				var i = 0,
				    len = latlngs.length;

				this.eachLayer(function (layer) {
					if (i < len) {
						layer.setLatLngs(latlngs[i++]);
					} else {
						this.removeLayer(layer);
					}
				}, this);

				while (i < len) {
					this.addLayer(new Klass(latlngs[i++], this._options));
				}

				return this;
			},

			getLatLngs: function () {
				var latlngs = [];

				this.eachLayer(function (layer) {
					latlngs.push(layer.getLatLngs());
				});

				return latlngs;
			}
		});
	}

	L.MultiPolyline = createMulti(L.Polyline);
	L.MultiPolygon = createMulti(L.Polygon);

	L.multiPolyline = function (latlngs, options) {
		return new L.MultiPolyline(latlngs, options);
	};

	L.multiPolygon = function (latlngs, options) {
		return new L.MultiPolygon(latlngs, options);
	};
}());


/*
 * L.Rectangle extends Polygon and creates a rectangle when passed a LatLngBounds object.
 */

L.Rectangle = L.Polygon.extend({
	initialize: function (latLngBounds, options) {
		L.Polygon.prototype.initialize.call(this, this._boundsToLatLngs(latLngBounds), options);
	},

	setBounds: function (latLngBounds) {
		this.setLatLngs(this._boundsToLatLngs(latLngBounds));
	},

	_boundsToLatLngs: function (latLngBounds) {
		latLngBounds = L.latLngBounds(latLngBounds);
		return [
			latLngBounds.getSouthWest(),
			latLngBounds.getNorthWest(),
			latLngBounds.getNorthEast(),
			latLngBounds.getSouthEast()
		];
	}
});

L.rectangle = function (latLngBounds, options) {
	return new L.Rectangle(latLngBounds, options);
};


/*
 * L.Circle is a circle overlay (with a certain radius in meters).
 */

L.Circle = L.Path.extend({
	initialize: function (latlng, radius, options) {
		L.Path.prototype.initialize.call(this, options);

		this._latlng = L.latLng(latlng);
		this._mRadius = radius;
	},

	options: {
		fill: true
	},

	setLatLng: function (latlng) {
		this._latlng = L.latLng(latlng);
		return this.redraw();
	},

	setRadius: function (radius) {
		this._mRadius = radius;
		return this.redraw();
	},

	projectLatlngs: function () {
		var lngRadius = this._getLngRadius(),
		    latlng = this._latlng,
		    pointLeft = this._map.latLngToLayerPoint([latlng.lat, latlng.lng - lngRadius]);

		this._point = this._map.latLngToLayerPoint(latlng);
		this._radius = Math.max(this._point.x - pointLeft.x, 1);
	},

	getBounds: function () {
		var lngRadius = this._getLngRadius(),
		    latRadius = (this._mRadius / 40075017) * 360,
		    latlng = this._latlng;

		return new L.LatLngBounds(
		        [latlng.lat - latRadius, latlng.lng - lngRadius],
		        [latlng.lat + latRadius, latlng.lng + lngRadius]);
	},

	getLatLng: function () {
		return this._latlng;
	},

	getPathString: function () {
		var p = this._point,
		    r = this._radius;

		if (this._checkIfEmpty()) {
			return '';
		}

		if (L.Browser.svg) {
			return 'M' + p.x + ',' + (p.y - r) +
			       'A' + r + ',' + r + ',0,1,1,' +
			       (p.x - 0.1) + ',' + (p.y - r) + ' z';
		} else {
			p._round();
			r = Math.round(r);
			return 'AL ' + p.x + ',' + p.y + ' ' + r + ',' + r + ' 0,' + (65535 * 360);
		}
	},

	getRadius: function () {
		return this._mRadius;
	},

	// TODO Earth hardcoded, move into projection code!

	_getLatRadius: function () {
		return (this._mRadius / 40075017) * 360;
	},

	_getLngRadius: function () {
		return this._getLatRadius() / Math.cos(L.LatLng.DEG_TO_RAD * this._latlng.lat);
	},

	_checkIfEmpty: function () {
		if (!this._map) {
			return false;
		}
		var vp = this._map._pathViewport,
		    r = this._radius,
		    p = this._point;

		return p.x - r > vp.max.x || p.y - r > vp.max.y ||
		       p.x + r < vp.min.x || p.y + r < vp.min.y;
	}
});

L.circle = function (latlng, radius, options) {
	return new L.Circle(latlng, radius, options);
};


/*
 * L.CircleMarker is a circle overlay with a permanent pixel radius.
 */

L.CircleMarker = L.Circle.extend({
	options: {
		radius: 10,
		weight: 2
	},

	initialize: function (latlng, options) {
		L.Circle.prototype.initialize.call(this, latlng, null, options);
		this._radius = this.options.radius;
	},

	projectLatlngs: function () {
		this._point = this._map.latLngToLayerPoint(this._latlng);
	},

	_updateStyle : function () {
		L.Circle.prototype._updateStyle.call(this);
		this.setRadius(this.options.radius);
	},

	setLatLng: function (latlng) {
		L.Circle.prototype.setLatLng.call(this, latlng);
		if (this._popup && this._popup._isOpen) {
			this._popup.setLatLng(latlng);
		}
		return this;
	},

	setRadius: function (radius) {
		this.options.radius = this._radius = radius;
		return this.redraw();
	},

	getRadius: function () {
		return this._radius;
	}
});

L.circleMarker = function (latlng, options) {
	return new L.CircleMarker(latlng, options);
};


/*
 * Extends L.Polyline to be able to manually detect clicks on Canvas-rendered polylines.
 */

L.Polyline.include(!L.Path.CANVAS ? {} : {
	_containsPoint: function (p, closed) {
		var i, j, k, len, len2, dist, part,
		    w = this.options.weight / 2;

		if (L.Browser.touch) {
			w += 10; // polyline click tolerance on touch devices
		}

		for (i = 0, len = this._parts.length; i < len; i++) {
			part = this._parts[i];
			for (j = 0, len2 = part.length, k = len2 - 1; j < len2; k = j++) {
				if (!closed && (j === 0)) {
					continue;
				}

				dist = L.LineUtil.pointToSegmentDistance(p, part[k], part[j]);

				if (dist <= w) {
					return true;
				}
			}
		}
		return false;
	}
});


/*
 * Extends L.Polygon to be able to manually detect clicks on Canvas-rendered polygons.
 */

L.Polygon.include(!L.Path.CANVAS ? {} : {
	_containsPoint: function (p) {
		var inside = false,
		    part, p1, p2,
		    i, j, k,
		    len, len2;

		// TODO optimization: check if within bounds first

		if (L.Polyline.prototype._containsPoint.call(this, p, true)) {
			// click on polygon border
			return true;
		}

		// ray casting algorithm for detecting if point is in polygon

		for (i = 0, len = this._parts.length; i < len; i++) {
			part = this._parts[i];

			for (j = 0, len2 = part.length, k = len2 - 1; j < len2; k = j++) {
				p1 = part[j];
				p2 = part[k];

				if (((p1.y > p.y) !== (p2.y > p.y)) &&
						(p.x < (p2.x - p1.x) * (p.y - p1.y) / (p2.y - p1.y) + p1.x)) {
					inside = !inside;
				}
			}
		}

		return inside;
	}
});


/*
 * Extends L.Circle with Canvas-specific code.
 */

L.Circle.include(!L.Path.CANVAS ? {} : {
	_drawPath: function () {
		var p = this._point;
		this._ctx.beginPath();
		this._ctx.arc(p.x, p.y, this._radius, 0, Math.PI * 2, false);
	},

	_containsPoint: function (p) {
		var center = this._point,
		    w2 = this.options.stroke ? this.options.weight / 2 : 0;

		return (p.distanceTo(center) <= this._radius + w2);
	}
});


/*
 * CircleMarker canvas specific drawing parts.
 */

L.CircleMarker.include(!L.Path.CANVAS ? {} : {
	_updateStyle: function () {
		L.Path.prototype._updateStyle.call(this);
	}
});


/*
 * L.GeoJSON turns any GeoJSON data into a Leaflet layer.
 */

L.GeoJSON = L.FeatureGroup.extend({

	initialize: function (geojson, options) {
		L.setOptions(this, options);

		this._layers = {};

		if (geojson) {
			this.addData(geojson);
		}
	},

	addData: function (geojson) {
		var features = L.Util.isArray(geojson) ? geojson : geojson.features,
		    i, len, feature;

		if (features) {
			for (i = 0, len = features.length; i < len; i++) {
				// Only add this if geometry or geometries are set and not null
				feature = features[i];
				if (feature.geometries || feature.geometry || feature.features || feature.coordinates) {
					this.addData(features[i]);
				}
			}
			return this;
		}

		var options = this.options;

		if (options.filter && !options.filter(geojson)) { return; }

		var layer = L.GeoJSON.geometryToLayer(geojson, options.pointToLayer, options.coordsToLatLng, options);
		layer.feature = L.GeoJSON.asFeature(geojson);

		layer.defaultOptions = layer.options;
		this.resetStyle(layer);

		if (options.onEachFeature) {
			options.onEachFeature(geojson, layer);
		}

		return this.addLayer(layer);
	},

	resetStyle: function (layer) {
		var style = this.options.style;
		if (style) {
			// reset any custom styles
			L.Util.extend(layer.options, layer.defaultOptions);

			this._setLayerStyle(layer, style);
		}
	},

	setStyle: function (style) {
		this.eachLayer(function (layer) {
			this._setLayerStyle(layer, style);
		}, this);
	},

	_setLayerStyle: function (layer, style) {
		if (typeof style === 'function') {
			style = style(layer.feature);
		}
		if (layer.setStyle) {
			layer.setStyle(style);
		}
	}
});

L.extend(L.GeoJSON, {
	geometryToLayer: function (geojson, pointToLayer, coordsToLatLng, vectorOptions) {
		var geometry = geojson.type === 'Feature' ? geojson.geometry : geojson,
		    coords = geometry.coordinates,
		    layers = [],
		    latlng, latlngs, i, len;

		coordsToLatLng = coordsToLatLng || this.coordsToLatLng;

		switch (geometry.type) {
		case 'Point':
			latlng = coordsToLatLng(coords);
			return pointToLayer ? pointToLayer(geojson, latlng) : new L.Marker(latlng);

		case 'MultiPoint':
			for (i = 0, len = coords.length; i < len; i++) {
				latlng = coordsToLatLng(coords[i]);
				layers.push(pointToLayer ? pointToLayer(geojson, latlng) : new L.Marker(latlng));
			}
			return new L.FeatureGroup(layers);

		case 'LineString':
			latlngs = this.coordsToLatLngs(coords, 0, coordsToLatLng);
			return new L.Polyline(latlngs, vectorOptions);

		case 'Polygon':
			if (coords.length === 2 && !coords[1].length) {
				throw new Error('Invalid GeoJSON object.');
			}
			latlngs = this.coordsToLatLngs(coords, 1, coordsToLatLng);
			return new L.Polygon(latlngs, vectorOptions);

		case 'MultiLineString':
			latlngs = this.coordsToLatLngs(coords, 1, coordsToLatLng);
			return new L.MultiPolyline(latlngs, vectorOptions);

		case 'MultiPolygon':
			latlngs = this.coordsToLatLngs(coords, 2, coordsToLatLng);
			return new L.MultiPolygon(latlngs, vectorOptions);

		case 'GeometryCollection':
			for (i = 0, len = geometry.geometries.length; i < len; i++) {

				layers.push(this.geometryToLayer({
					geometry: geometry.geometries[i],
					type: 'Feature',
					properties: geojson.properties
				}, pointToLayer, coordsToLatLng, vectorOptions));
			}
			return new L.FeatureGroup(layers);

		default:
			throw new Error('Invalid GeoJSON object.');
		}
	},

	coordsToLatLng: function (coords) { // (Array[, Boolean]) -> LatLng
		return new L.LatLng(coords[1], coords[0], coords[2]);
	},

	coordsToLatLngs: function (coords, levelsDeep, coordsToLatLng) { // (Array[, Number, Function]) -> Array
		var latlng, i, len,
		    latlngs = [];

		for (i = 0, len = coords.length; i < len; i++) {
			latlng = levelsDeep ?
			        this.coordsToLatLngs(coords[i], levelsDeep - 1, coordsToLatLng) :
			        (coordsToLatLng || this.coordsToLatLng)(coords[i]);

			latlngs.push(latlng);
		}

		return latlngs;
	},

	latLngToCoords: function (latlng) {
		var coords = [latlng.lng, latlng.lat];

		if (latlng.alt !== undefined) {
			coords.push(latlng.alt);
		}
		return coords;
	},

	latLngsToCoords: function (latLngs) {
		var coords = [];

		for (var i = 0, len = latLngs.length; i < len; i++) {
			coords.push(L.GeoJSON.latLngToCoords(latLngs[i]));
		}

		return coords;
	},

	getFeature: function (layer, newGeometry) {
		return layer.feature ? L.extend({}, layer.feature, {geometry: newGeometry}) : L.GeoJSON.asFeature(newGeometry);
	},

	asFeature: function (geoJSON) {
		if (geoJSON.type === 'Feature') {
			return geoJSON;
		}

		return {
			type: 'Feature',
			properties: {},
			geometry: geoJSON
		};
	}
});

var PointToGeoJSON = {
	toGeoJSON: function () {
		return L.GeoJSON.getFeature(this, {
			type: 'Point',
			coordinates: L.GeoJSON.latLngToCoords(this.getLatLng())
		});
	}
};

L.Marker.include(PointToGeoJSON);
L.Circle.include(PointToGeoJSON);
L.CircleMarker.include(PointToGeoJSON);

L.Polyline.include({
	toGeoJSON: function () {
		return L.GeoJSON.getFeature(this, {
			type: 'LineString',
			coordinates: L.GeoJSON.latLngsToCoords(this.getLatLngs())
		});
	}
});

L.Polygon.include({
	toGeoJSON: function () {
		var coords = [L.GeoJSON.latLngsToCoords(this.getLatLngs())],
		    i, len, hole;

		coords[0].push(coords[0][0]);

		if (this._holes) {
			for (i = 0, len = this._holes.length; i < len; i++) {
				hole = L.GeoJSON.latLngsToCoords(this._holes[i]);
				hole.push(hole[0]);
				coords.push(hole);
			}
		}

		return L.GeoJSON.getFeature(this, {
			type: 'Polygon',
			coordinates: coords
		});
	}
});

(function () {
	function multiToGeoJSON(type) {
		return function () {
			var coords = [];

			this.eachLayer(function (layer) {
				coords.push(layer.toGeoJSON().geometry.coordinates);
			});

			return L.GeoJSON.getFeature(this, {
				type: type,
				coordinates: coords
			});
		};
	}

	L.MultiPolyline.include({toGeoJSON: multiToGeoJSON('MultiLineString')});
	L.MultiPolygon.include({toGeoJSON: multiToGeoJSON('MultiPolygon')});

	L.LayerGroup.include({
		toGeoJSON: function () {

			var geometry = this.feature && this.feature.geometry,
				jsons = [],
				json;

			if (geometry && geometry.type === 'MultiPoint') {
				return multiToGeoJSON('MultiPoint').call(this);
			}

			var isGeometryCollection = geometry && geometry.type === 'GeometryCollection';

			this.eachLayer(function (layer) {
				if (layer.toGeoJSON) {
					json = layer.toGeoJSON();
					jsons.push(isGeometryCollection ? json.geometry : L.GeoJSON.asFeature(json));
				}
			});

			if (isGeometryCollection) {
				return L.GeoJSON.getFeature(this, {
					geometries: jsons,
					type: 'GeometryCollection'
				});
			}

			return {
				type: 'FeatureCollection',
				features: jsons
			};
		}
	});
}());

L.geoJson = function (geojson, options) {
	return new L.GeoJSON(geojson, options);
};


/*
 * L.DomEvent contains functions for working with DOM events.
 */

L.DomEvent = {
	/* inspired by John Resig, Dean Edwards and YUI addEvent implementations */
	addListener: function (obj, type, fn, context) { // (HTMLElement, String, Function[, Object])

		var id = L.stamp(fn),
		    key = '_leaflet_' + type + id,
		    handler, originalHandler, newType;

		if (obj[key]) { return this; }

		handler = function (e) {
			return fn.call(context || obj, e || L.DomEvent._getEvent());
		};

		if (L.Browser.pointer && type.indexOf('touch') === 0) {
			return this.addPointerListener(obj, type, handler, id);
		}
		if (L.Browser.touch && (type === 'dblclick') && this.addDoubleTapListener) {
			this.addDoubleTapListener(obj, handler, id);
		}

		if ('addEventListener' in obj) {

			if (type === 'mousewheel') {
				obj.addEventListener('DOMMouseScroll', handler, false);
				obj.addEventListener(type, handler, false);

			} else if ((type === 'mouseenter') || (type === 'mouseleave')) {

				originalHandler = handler;
				newType = (type === 'mouseenter' ? 'mouseover' : 'mouseout');

				handler = function (e) {
					if (!L.DomEvent._checkMouse(obj, e)) { return; }
					return originalHandler(e);
				};

				obj.addEventListener(newType, handler, false);

			} else if (type === 'click' && L.Browser.android) {
				originalHandler = handler;
				handler = function (e) {
					return L.DomEvent._filterClick(e, originalHandler);
				};

				obj.addEventListener(type, handler, false);
			} else {
				obj.addEventListener(type, handler, false);
			}

		} else if ('attachEvent' in obj) {
			obj.attachEvent('on' + type, handler);
		}

		obj[key] = handler;

		return this;
	},

	removeListener: function (obj, type, fn) {  // (HTMLElement, String, Function)

		var id = L.stamp(fn),
		    key = '_leaflet_' + type + id,
		    handler = obj[key];

		if (!handler) { return this; }

		if (L.Browser.pointer && type.indexOf('touch') === 0) {
			this.removePointerListener(obj, type, id);
		} else if (L.Browser.touch && (type === 'dblclick') && this.removeDoubleTapListener) {
			this.removeDoubleTapListener(obj, id);

		} else if ('removeEventListener' in obj) {

			if (type === 'mousewheel') {
				obj.removeEventListener('DOMMouseScroll', handler, false);
				obj.removeEventListener(type, handler, false);

			} else if ((type === 'mouseenter') || (type === 'mouseleave')) {
				obj.removeEventListener((type === 'mouseenter' ? 'mouseover' : 'mouseout'), handler, false);
			} else {
				obj.removeEventListener(type, handler, false);
			}
		} else if ('detachEvent' in obj) {
			obj.detachEvent('on' + type, handler);
		}

		obj[key] = null;

		return this;
	},

	stopPropagation: function (e) {

		if (e.stopPropagation) {
			e.stopPropagation();
		} else {
			e.cancelBubble = true;
		}
		L.DomEvent._skipped(e);

		return this;
	},

	disableScrollPropagation: function (el) {
		var stop = L.DomEvent.stopPropagation;

		return L.DomEvent
			.on(el, 'mousewheel', stop)
			.on(el, 'MozMousePixelScroll', stop);
	},

	disableClickPropagation: function (el) {
		var stop = L.DomEvent.stopPropagation;

		for (var i = L.Draggable.START.length - 1; i >= 0; i--) {
			L.DomEvent.on(el, L.Draggable.START[i], stop);
		}

		return L.DomEvent
			.on(el, 'click', L.DomEvent._fakeStop)
			.on(el, 'dblclick', stop);
	},

	preventDefault: function (e) {

		if (e.preventDefault) {
			e.preventDefault();
		} else {
			e.returnValue = false;
		}
		return this;
	},

	stop: function (e) {
		return L.DomEvent
			.preventDefault(e)
			.stopPropagation(e);
	},

	getMousePosition: function (e, container) {
		if (!container) {
			return new L.Point(e.clientX, e.clientY);
		}

		var rect = container.getBoundingClientRect();

		return new L.Point(
			e.clientX - rect.left - container.clientLeft,
			e.clientY - rect.top - container.clientTop);
	},

	getWheelDelta: function (e) {

		var delta = 0;

		if (e.wheelDelta) {
			delta = e.wheelDelta / 120;
		}
		if (e.detail) {
			delta = -e.detail / 3;
		}
		return delta;
	},

	_skipEvents: {},

	_fakeStop: function (e) {
		// fakes stopPropagation by setting a special event flag, checked/reset with L.DomEvent._skipped(e)
		L.DomEvent._skipEvents[e.type] = true;
	},

	_skipped: function (e) {
		var skipped = this._skipEvents[e.type];
		// reset when checking, as it's only used in map container and propagates outside of the map
		this._skipEvents[e.type] = false;
		return skipped;
	},

	// check if element really left/entered the event target (for mouseenter/mouseleave)
	_checkMouse: function (el, e) {

		var related = e.relatedTarget;

		if (!related) { return true; }

		try {
			while (related && (related !== el)) {
				related = related.parentNode;
			}
		} catch (err) {
			return false;
		}
		return (related !== el);
	},

	_getEvent: function () { // evil magic for IE
		/*jshint noarg:false */
		var e = window.event;
		if (!e) {
			var caller = arguments.callee.caller;
			while (caller) {
				e = caller['arguments'][0];
				if (e && window.Event === e.constructor) {
					break;
				}
				caller = caller.caller;
			}
		}
		return e;
	},

	// this is a horrible workaround for a bug in Android where a single touch triggers two click events
	_filterClick: function (e, handler) {
		var timeStamp = (e.timeStamp || e.originalEvent.timeStamp),
			elapsed = L.DomEvent._lastClick && (timeStamp - L.DomEvent._lastClick);

		// are they closer together than 500ms yet more than 100ms?
		// Android typically triggers them ~300ms apart while multiple listeners
		// on the same event should be triggered far faster;
		// or check if click is simulated on the element, and if it is, reject any non-simulated events

		if ((elapsed && elapsed > 100 && elapsed < 500) || (e.target._simulatedClick && !e._simulated)) {
			L.DomEvent.stop(e);
			return;
		}
		L.DomEvent._lastClick = timeStamp;

		return handler(e);
	}
};

L.DomEvent.on = L.DomEvent.addListener;
L.DomEvent.off = L.DomEvent.removeListener;


/*
 * L.Draggable allows you to add dragging capabilities to any element. Supports mobile devices too.
 */

L.Draggable = L.Class.extend({
	includes: L.Mixin.Events,

	statics: {
		START: L.Browser.touch ? ['touchstart', 'mousedown'] : ['mousedown'],
		END: {
			mousedown: 'mouseup',
			touchstart: 'touchend',
			pointerdown: 'touchend',
			MSPointerDown: 'touchend'
		},
		MOVE: {
			mousedown: 'mousemove',
			touchstart: 'touchmove',
			pointerdown: 'touchmove',
			MSPointerDown: 'touchmove'
		}
	},

	initialize: function (element, dragStartTarget) {
		this._element = element;
		this._dragStartTarget = dragStartTarget || element;
	},

	enable: function () {
		if (this._enabled) { return; }

		for (var i = L.Draggable.START.length - 1; i >= 0; i--) {
			L.DomEvent.on(this._dragStartTarget, L.Draggable.START[i], this._onDown, this);
		}

		this._enabled = true;
	},

	disable: function () {
		if (!this._enabled) { return; }

		for (var i = L.Draggable.START.length - 1; i >= 0; i--) {
			L.DomEvent.off(this._dragStartTarget, L.Draggable.START[i], this._onDown, this);
		}

		this._enabled = false;
		this._moved = false;
	},

	_onDown: function (e) {
		this._moved = false;

		if (e.shiftKey || ((e.which !== 1) && (e.button !== 1) && !e.touches)) { return; }

		L.DomEvent.stopPropagation(e);

		if (L.Draggable._disabled) { return; }

		L.DomUtil.disableImageDrag();
		L.DomUtil.disableTextSelection();

		if (this._moving) { return; }

		var first = e.touches ? e.touches[0] : e;

		this._startPoint = new L.Point(first.clientX, first.clientY);
		this._startPos = this._newPos = L.DomUtil.getPosition(this._element);

		L.DomEvent
		    .on(document, L.Draggable.MOVE[e.type], this._onMove, this)
		    .on(document, L.Draggable.END[e.type], this._onUp, this);
	},

	_onMove: function (e) {
		if (e.touches && e.touches.length > 1) {
			this._moved = true;
			return;
		}

		var first = (e.touches && e.touches.length === 1 ? e.touches[0] : e),
		    newPoint = new L.Point(first.clientX, first.clientY),
		    offset = newPoint.subtract(this._startPoint);

		if (!offset.x && !offset.y) { return; }
		if (L.Browser.touch && Math.abs(offset.x) + Math.abs(offset.y) < 3) { return; }

		L.DomEvent.preventDefault(e);

		if (!this._moved) {
			this.fire('dragstart');

			this._moved = true;
			this._startPos = L.DomUtil.getPosition(this._element).subtract(offset);

			L.DomUtil.addClass(document.body, 'leaflet-dragging');
			this._lastTarget = e.target || e.srcElement;
			L.DomUtil.addClass(this._lastTarget, 'leaflet-drag-target');
		}

		this._newPos = this._startPos.add(offset);
		this._moving = true;

		L.Util.cancelAnimFrame(this._animRequest);
		this._animRequest = L.Util.requestAnimFrame(this._updatePosition, this, true, this._dragStartTarget);
	},

	_updatePosition: function () {
		this.fire('predrag');
		L.DomUtil.setPosition(this._element, this._newPos);
		this.fire('drag');
	},

	_onUp: function () {
		L.DomUtil.removeClass(document.body, 'leaflet-dragging');

		if (this._lastTarget) {
			L.DomUtil.removeClass(this._lastTarget, 'leaflet-drag-target');
			this._lastTarget = null;
		}

		for (var i in L.Draggable.MOVE) {
			L.DomEvent
			    .off(document, L.Draggable.MOVE[i], this._onMove)
			    .off(document, L.Draggable.END[i], this._onUp);
		}

		L.DomUtil.enableImageDrag();
		L.DomUtil.enableTextSelection();

		if (this._moved && this._moving) {
			// ensure drag is not fired after dragend
			L.Util.cancelAnimFrame(this._animRequest);

			this.fire('dragend', {
				distance: this._newPos.distanceTo(this._startPos)
			});
		}

		this._moving = false;
	}
});


/*
	L.Handler is a base class for handler classes that are used internally to inject
	interaction features like dragging to classes like Map and Marker.
*/

L.Handler = L.Class.extend({
	initialize: function (map) {
		this._map = map;
	},

	enable: function () {
		if (this._enabled) { return; }

		this._enabled = true;
		this.addHooks();
	},

	disable: function () {
		if (!this._enabled) { return; }

		this._enabled = false;
		this.removeHooks();
	},

	enabled: function () {
		return !!this._enabled;
	}
});


/*
 * L.Handler.MapDrag is used to make the map draggable (with panning inertia), enabled by default.
 */

L.Map.mergeOptions({
	dragging: true,

	inertia: !L.Browser.android23,
	inertiaDeceleration: 3400, // px/s^2
	inertiaMaxSpeed: Infinity, // px/s
	inertiaThreshold: L.Browser.touch ? 32 : 18, // ms
	easeLinearity: 0.25,

	// TODO refactor, move to CRS
	worldCopyJump: false
});

L.Map.Drag = L.Handler.extend({
	addHooks: function () {
		if (!this._draggable) {
			var map = this._map;

			this._draggable = new L.Draggable(map._mapPane, map._container);

			this._draggable.on({
				'dragstart': this._onDragStart,
				'drag': this._onDrag,
				'dragend': this._onDragEnd
			}, this);

			if (map.options.worldCopyJump) {
				this._draggable.on('predrag', this._onPreDrag, this);
				map.on('viewreset', this._onViewReset, this);

				map.whenReady(this._onViewReset, this);
			}
		}
		this._draggable.enable();
	},

	removeHooks: function () {
		this._draggable.disable();
	},

	moved: function () {
		return this._draggable && this._draggable._moved;
	},

	_onDragStart: function () {
		var map = this._map;

		if (map._panAnim) {
			map._panAnim.stop();
		}

		map
		    .fire('movestart')
		    .fire('dragstart');

		if (map.options.inertia) {
			this._positions = [];
			this._times = [];
		}
	},

	_onDrag: function () {
		if (this._map.options.inertia) {
			var time = this._lastTime = +new Date(),
			    pos = this._lastPos = this._draggable._newPos;

			this._positions.push(pos);
			this._times.push(time);

			if (time - this._times[0] > 200) {
				this._positions.shift();
				this._times.shift();
			}
		}

		this._map
		    .fire('move')
		    .fire('drag');
	},

	_onViewReset: function () {
		// TODO fix hardcoded Earth values
		var pxCenter = this._map.getSize()._divideBy(2),
		    pxWorldCenter = this._map.latLngToLayerPoint([0, 0]);

		this._initialWorldOffset = pxWorldCenter.subtract(pxCenter).x;
		this._worldWidth = this._map.project([0, 180]).x;
	},

	_onPreDrag: function () {
		// TODO refactor to be able to adjust map pane position after zoom
		var worldWidth = this._worldWidth,
		    halfWidth = Math.round(worldWidth / 2),
		    dx = this._initialWorldOffset,
		    x = this._draggable._newPos.x,
		    newX1 = (x - halfWidth + dx) % worldWidth + halfWidth - dx,
		    newX2 = (x + halfWidth + dx) % worldWidth - halfWidth - dx,
		    newX = Math.abs(newX1 + dx) < Math.abs(newX2 + dx) ? newX1 : newX2;

		this._draggable._newPos.x = newX;
	},

	_onDragEnd: function (e) {
		var map = this._map,
		    options = map.options,
		    delay = +new Date() - this._lastTime,

		    noInertia = !options.inertia || delay > options.inertiaThreshold || !this._positions[0];

		map.fire('dragend', e);

		if (noInertia) {
			map.fire('moveend');

		} else {

			var direction = this._lastPos.subtract(this._positions[0]),
			    duration = (this._lastTime + delay - this._times[0]) / 1000,
			    ease = options.easeLinearity,

			    speedVector = direction.multiplyBy(ease / duration),
			    speed = speedVector.distanceTo([0, 0]),

			    limitedSpeed = Math.min(options.inertiaMaxSpeed, speed),
			    limitedSpeedVector = speedVector.multiplyBy(limitedSpeed / speed),

			    decelerationDuration = limitedSpeed / (options.inertiaDeceleration * ease),
			    offset = limitedSpeedVector.multiplyBy(-decelerationDuration / 2).round();

			if (!offset.x || !offset.y) {
				map.fire('moveend');

			} else {
				offset = map._limitOffset(offset, map.options.maxBounds);

				L.Util.requestAnimFrame(function () {
					map.panBy(offset, {
						duration: decelerationDuration,
						easeLinearity: ease,
						noMoveStart: true
					});
				});
			}
		}
	}
});

L.Map.addInitHook('addHandler', 'dragging', L.Map.Drag);


/*
 * L.Handler.DoubleClickZoom is used to handle double-click zoom on the map, enabled by default.
 */

L.Map.mergeOptions({
	doubleClickZoom: true
});

L.Map.DoubleClickZoom = L.Handler.extend({
	addHooks: function () {
		this._map.on('dblclick', this._onDoubleClick, this);
	},

	removeHooks: function () {
		this._map.off('dblclick', this._onDoubleClick, this);
	},

	_onDoubleClick: function (e) {
		var map = this._map,
		    zoom = map.getZoom() + (e.originalEvent.shiftKey ? -1 : 1);

		if (map.options.doubleClickZoom === 'center') {
			map.setZoom(zoom);
		} else {
			map.setZoomAround(e.containerPoint, zoom);
		}
	}
});

L.Map.addInitHook('addHandler', 'doubleClickZoom', L.Map.DoubleClickZoom);


/*
 * L.Handler.ScrollWheelZoom is used by L.Map to enable mouse scroll wheel zoom on the map.
 */

L.Map.mergeOptions({
	scrollWheelZoom: true
});

L.Map.ScrollWheelZoom = L.Handler.extend({
	addHooks: function () {
		L.DomEvent.on(this._map._container, 'mousewheel', this._onWheelScroll, this);
		L.DomEvent.on(this._map._container, 'MozMousePixelScroll', L.DomEvent.preventDefault);
		this._delta = 0;
	},

	removeHooks: function () {
		L.DomEvent.off(this._map._container, 'mousewheel', this._onWheelScroll);
		L.DomEvent.off(this._map._container, 'MozMousePixelScroll', L.DomEvent.preventDefault);
	},

	_onWheelScroll: function (e) {
		var delta = L.DomEvent.getWheelDelta(e);

		this._delta += delta;
		this._lastMousePos = this._map.mouseEventToContainerPoint(e);

		if (!this._startTime) {
			this._startTime = +new Date();
		}

		var left = Math.max(40 - (+new Date() - this._startTime), 0);

		clearTimeout(this._timer);
		this._timer = setTimeout(L.bind(this._performZoom, this), left);

		L.DomEvent.preventDefault(e);
		L.DomEvent.stopPropagation(e);
	},

	_performZoom: function () {
		var map = this._map,
		    delta = this._delta,
		    zoom = map.getZoom();

		delta = delta > 0 ? Math.ceil(delta) : Math.floor(delta);
		delta = Math.max(Math.min(delta, 4), -4);
		delta = map._limitZoom(zoom + delta) - zoom;

		this._delta = 0;
		this._startTime = null;

		if (!delta) { return; }

		if (map.options.scrollWheelZoom === 'center') {
			map.setZoom(zoom + delta);
		} else {
			map.setZoomAround(this._lastMousePos, zoom + delta);
		}
	}
});

L.Map.addInitHook('addHandler', 'scrollWheelZoom', L.Map.ScrollWheelZoom);


/*
 * Extends the event handling code with double tap support for mobile browsers.
 */

L.extend(L.DomEvent, {

	_touchstart: L.Browser.msPointer ? 'MSPointerDown' : L.Browser.pointer ? 'pointerdown' : 'touchstart',
	_touchend: L.Browser.msPointer ? 'MSPointerUp' : L.Browser.pointer ? 'pointerup' : 'touchend',

	// inspired by Zepto touch code by Thomas Fuchs
	addDoubleTapListener: function (obj, handler, id) {
		var last,
		    doubleTap = false,
		    delay = 250,
		    touch,
		    pre = '_leaflet_',
		    touchstart = this._touchstart,
		    touchend = this._touchend,
		    trackedTouches = [];

		function onTouchStart(e) {
			var count;

			if (L.Browser.pointer) {
				trackedTouches.push(e.pointerId);
				count = trackedTouches.length;
			} else {
				count = e.touches.length;
			}
			if (count > 1) {
				return;
			}

			var now = Date.now(),
				delta = now - (last || now);

			touch = e.touches ? e.touches[0] : e;
			doubleTap = (delta > 0 && delta <= delay);
			last = now;
		}

		function onTouchEnd(e) {
			if (L.Browser.pointer) {
				var idx = trackedTouches.indexOf(e.pointerId);
				if (idx === -1) {
					return;
				}
				trackedTouches.splice(idx, 1);
			}

			if (doubleTap) {
				if (L.Browser.pointer) {
					// work around .type being readonly with MSPointer* events
					var newTouch = { },
						prop;

					// jshint forin:false
					for (var i in touch) {
						prop = touch[i];
						if (typeof prop === 'function') {
							newTouch[i] = prop.bind(touch);
						} else {
							newTouch[i] = prop;
						}
					}
					touch = newTouch;
				}
				touch.type = 'dblclick';
				handler(touch);
				last = null;
			}
		}
		obj[pre + touchstart + id] = onTouchStart;
		obj[pre + touchend + id] = onTouchEnd;

		// on pointer we need to listen on the document, otherwise a drag starting on the map and moving off screen
		// will not come through to us, so we will lose track of how many touches are ongoing
		var endElement = L.Browser.pointer ? document.documentElement : obj;

		obj.addEventListener(touchstart, onTouchStart, false);
		endElement.addEventListener(touchend, onTouchEnd, false);

		if (L.Browser.pointer) {
			endElement.addEventListener(L.DomEvent.POINTER_CANCEL, onTouchEnd, false);
		}

		return this;
	},

	removeDoubleTapListener: function (obj, id) {
		var pre = '_leaflet_';

		obj.removeEventListener(this._touchstart, obj[pre + this._touchstart + id], false);
		(L.Browser.pointer ? document.documentElement : obj).removeEventListener(
		        this._touchend, obj[pre + this._touchend + id], false);

		if (L.Browser.pointer) {
			document.documentElement.removeEventListener(L.DomEvent.POINTER_CANCEL, obj[pre + this._touchend + id],
				false);
		}

		return this;
	}
});


/*
 * Extends L.DomEvent to provide touch support for Internet Explorer and Windows-based devices.
 */

L.extend(L.DomEvent, {

	//static
	POINTER_DOWN: L.Browser.msPointer ? 'MSPointerDown' : 'pointerdown',
	POINTER_MOVE: L.Browser.msPointer ? 'MSPointerMove' : 'pointermove',
	POINTER_UP: L.Browser.msPointer ? 'MSPointerUp' : 'pointerup',
	POINTER_CANCEL: L.Browser.msPointer ? 'MSPointerCancel' : 'pointercancel',

	_pointers: [],
	_pointerDocumentListener: false,

	// Provides a touch events wrapper for (ms)pointer events.
	// Based on changes by veproza https://github.com/CloudMade/Leaflet/pull/1019
	//ref http://www.w3.org/TR/pointerevents/ https://www.w3.org/Bugs/Public/show_bug.cgi?id=22890

	addPointerListener: function (obj, type, handler, id) {

		switch (type) {
		case 'touchstart':
			return this.addPointerListenerStart(obj, type, handler, id);
		case 'touchend':
			return this.addPointerListenerEnd(obj, type, handler, id);
		case 'touchmove':
			return this.addPointerListenerMove(obj, type, handler, id);
		default:
			throw 'Unknown touch event type';
		}
	},

	addPointerListenerStart: function (obj, type, handler, id) {
		var pre = '_leaflet_',
		    pointers = this._pointers;

		var cb = function (e) {
			if (e.pointerType !== 'mouse' && e.pointerType !== e.MSPOINTER_TYPE_MOUSE) {
				L.DomEvent.preventDefault(e);
			}

			var alreadyInArray = false;
			for (var i = 0; i < pointers.length; i++) {
				if (pointers[i].pointerId === e.pointerId) {
					alreadyInArray = true;
					break;
				}
			}
			if (!alreadyInArray) {
				pointers.push(e);
			}

			e.touches = pointers.slice();
			e.changedTouches = [e];

			handler(e);
		};

		obj[pre + 'touchstart' + id] = cb;
		obj.addEventListener(this.POINTER_DOWN, cb, false);

		// need to also listen for end events to keep the _pointers list accurate
		// this needs to be on the body and never go away
		if (!this._pointerDocumentListener) {
			var internalCb = function (e) {
				for (var i = 0; i < pointers.length; i++) {
					if (pointers[i].pointerId === e.pointerId) {
						pointers.splice(i, 1);
						break;
					}
				}
			};
			//We listen on the documentElement as any drags that end by moving the touch off the screen get fired there
			document.documentElement.addEventListener(this.POINTER_UP, internalCb, false);
			document.documentElement.addEventListener(this.POINTER_CANCEL, internalCb, false);

			this._pointerDocumentListener = true;
		}

		return this;
	},

	addPointerListenerMove: function (obj, type, handler, id) {
		var pre = '_leaflet_',
		    touches = this._pointers;

		function cb(e) {

			// don't fire touch moves when mouse isn't down
			if ((e.pointerType === e.MSPOINTER_TYPE_MOUSE || e.pointerType === 'mouse') && e.buttons === 0) { return; }

			for (var i = 0; i < touches.length; i++) {
				if (touches[i].pointerId === e.pointerId) {
					touches[i] = e;
					break;
				}
			}

			e.touches = touches.slice();
			e.changedTouches = [e];

			handler(e);
		}

		obj[pre + 'touchmove' + id] = cb;
		obj.addEventListener(this.POINTER_MOVE, cb, false);

		return this;
	},

	addPointerListenerEnd: function (obj, type, handler, id) {
		var pre = '_leaflet_',
		    touches = this._pointers;

		var cb = function (e) {
			for (var i = 0; i < touches.length; i++) {
				if (touches[i].pointerId === e.pointerId) {
					touches.splice(i, 1);
					break;
				}
			}

			e.touches = touches.slice();
			e.changedTouches = [e];

			handler(e);
		};

		obj[pre + 'touchend' + id] = cb;
		obj.addEventListener(this.POINTER_UP, cb, false);
		obj.addEventListener(this.POINTER_CANCEL, cb, false);

		return this;
	},

	removePointerListener: function (obj, type, id) {
		var pre = '_leaflet_',
		    cb = obj[pre + type + id];

		switch (type) {
		case 'touchstart':
			obj.removeEventListener(this.POINTER_DOWN, cb, false);
			break;
		case 'touchmove':
			obj.removeEventListener(this.POINTER_MOVE, cb, false);
			break;
		case 'touchend':
			obj.removeEventListener(this.POINTER_UP, cb, false);
			obj.removeEventListener(this.POINTER_CANCEL, cb, false);
			break;
		}

		return this;
	}
});


/*
 * L.Handler.TouchZoom is used by L.Map to add pinch zoom on supported mobile browsers.
 */

L.Map.mergeOptions({
	touchZoom: L.Browser.touch && !L.Browser.android23,
	bounceAtZoomLimits: true
});

L.Map.TouchZoom = L.Handler.extend({
	addHooks: function () {
		L.DomEvent.on(this._map._container, 'touchstart', this._onTouchStart, this);
	},

	removeHooks: function () {
		L.DomEvent.off(this._map._container, 'touchstart', this._onTouchStart, this);
	},

	_onTouchStart: function (e) {
		var map = this._map;

		if (!e.touches || e.touches.length !== 2 || map._animatingZoom || this._zooming) { return; }

		var p1 = map.mouseEventToLayerPoint(e.touches[0]),
		    p2 = map.mouseEventToLayerPoint(e.touches[1]),
		    viewCenter = map._getCenterLayerPoint();

		this._startCenter = p1.add(p2)._divideBy(2);
		this._startDist = p1.distanceTo(p2);

		this._moved = false;
		this._zooming = true;

		this._centerOffset = viewCenter.subtract(this._startCenter);

		if (map._panAnim) {
			map._panAnim.stop();
		}

		L.DomEvent
		    .on(document, 'touchmove', this._onTouchMove, this)
		    .on(document, 'touchend', this._onTouchEnd, this);

		L.DomEvent.preventDefault(e);
	},

	_onTouchMove: function (e) {
		var map = this._map;

		if (!e.touches || e.touches.length !== 2 || !this._zooming) { return; }

		var p1 = map.mouseEventToLayerPoint(e.touches[0]),
		    p2 = map.mouseEventToLayerPoint(e.touches[1]);

		this._scale = p1.distanceTo(p2) / this._startDist;
		this._delta = p1._add(p2)._divideBy(2)._subtract(this._startCenter);

		if (this._scale === 1) { return; }

		if (!map.options.bounceAtZoomLimits) {
			if ((map.getZoom() === map.getMinZoom() && this._scale < 1) ||
			    (map.getZoom() === map.getMaxZoom() && this._scale > 1)) { return; }
		}

		if (!this._moved) {
			L.DomUtil.addClass(map._mapPane, 'leaflet-touching');

			map
			    .fire('movestart')
			    .fire('zoomstart');

			this._moved = true;
		}

		L.Util.cancelAnimFrame(this._animRequest);
		this._animRequest = L.Util.requestAnimFrame(
		        this._updateOnMove, this, true, this._map._container);

		L.DomEvent.preventDefault(e);
	},

	_updateOnMove: function () {
		var map = this._map,
		    origin = this._getScaleOrigin(),
		    center = map.layerPointToLatLng(origin),
		    zoom = map.getScaleZoom(this._scale);

		map._animateZoom(center, zoom, this._startCenter, this._scale, this._delta, false, true);
	},

	_onTouchEnd: function () {
		if (!this._moved || !this._zooming) {
			this._zooming = false;
			return;
		}

		var map = this._map;

		this._zooming = false;
		L.DomUtil.removeClass(map._mapPane, 'leaflet-touching');
		L.Util.cancelAnimFrame(this._animRequest);

		L.DomEvent
		    .off(document, 'touchmove', this._onTouchMove)
		    .off(document, 'touchend', this._onTouchEnd);

		var origin = this._getScaleOrigin(),
		    center = map.layerPointToLatLng(origin),

		    oldZoom = map.getZoom(),
		    floatZoomDelta = map.getScaleZoom(this._scale) - oldZoom,
		    roundZoomDelta = (floatZoomDelta > 0 ?
		            Math.ceil(floatZoomDelta) : Math.floor(floatZoomDelta)),

		    zoom = map._limitZoom(oldZoom + roundZoomDelta),
		    scale = map.getZoomScale(zoom) / this._scale;

		map._animateZoom(center, zoom, origin, scale);
	},

	_getScaleOrigin: function () {
		var centerOffset = this._centerOffset.subtract(this._delta).divideBy(this._scale);
		return this._startCenter.add(centerOffset);
	}
});

L.Map.addInitHook('addHandler', 'touchZoom', L.Map.TouchZoom);


/*
 * L.Map.Tap is used to enable mobile hacks like quick taps and long hold.
 */

L.Map.mergeOptions({
	tap: true,
	tapTolerance: 15
});

L.Map.Tap = L.Handler.extend({
	addHooks: function () {
		L.DomEvent.on(this._map._container, 'touchstart', this._onDown, this);
	},

	removeHooks: function () {
		L.DomEvent.off(this._map._container, 'touchstart', this._onDown, this);
	},

	_onDown: function (e) {
		if (!e.touches) { return; }

		L.DomEvent.preventDefault(e);

		this._fireClick = true;

		// don't simulate click or track longpress if more than 1 touch
		if (e.touches.length > 1) {
			this._fireClick = false;
			clearTimeout(this._holdTimeout);
			return;
		}

		var first = e.touches[0],
		    el = first.target;

		this._startPos = this._newPos = new L.Point(first.clientX, first.clientY);

		// if touching a link, highlight it
		if (el.tagName && el.tagName.toLowerCase() === 'a') {
			L.DomUtil.addClass(el, 'leaflet-active');
		}

		// simulate long hold but setting a timeout
		this._holdTimeout = setTimeout(L.bind(function () {
			if (this._isTapValid()) {
				this._fireClick = false;
				this._onUp();
				this._simulateEvent('contextmenu', first);
			}
		}, this), 1000);

		L.DomEvent
			.on(document, 'touchmove', this._onMove, this)
			.on(document, 'touchend', this._onUp, this);
	},

	_onUp: function (e) {
		clearTimeout(this._holdTimeout);

		L.DomEvent
			.off(document, 'touchmove', this._onMove, this)
			.off(document, 'touchend', this._onUp, this);

		if (this._fireClick && e && e.changedTouches) {

			var first = e.changedTouches[0],
			    el = first.target;

			if (el && el.tagName && el.tagName.toLowerCase() === 'a') {
				L.DomUtil.removeClass(el, 'leaflet-active');
			}

			// simulate click if the touch didn't move too much
			if (this._isTapValid()) {
				this._simulateEvent('click', first);
			}
		}
	},

	_isTapValid: function () {
		return this._newPos.distanceTo(this._startPos) <= this._map.options.tapTolerance;
	},

	_onMove: function (e) {
		var first = e.touches[0];
		this._newPos = new L.Point(first.clientX, first.clientY);
	},

	_simulateEvent: function (type, e) {
		var simulatedEvent = document.createEvent('MouseEvents');

		simulatedEvent._simulated = true;
		e.target._simulatedClick = true;

		simulatedEvent.initMouseEvent(
		        type, true, true, window, 1,
		        e.screenX, e.screenY,
		        e.clientX, e.clientY,
		        false, false, false, false, 0, null);

		e.target.dispatchEvent(simulatedEvent);
	}
});

if (L.Browser.touch && !L.Browser.pointer) {
	L.Map.addInitHook('addHandler', 'tap', L.Map.Tap);
}


/*
 * L.Handler.ShiftDragZoom is used to add shift-drag zoom interaction to the map
  * (zoom to a selected bounding box), enabled by default.
 */

L.Map.mergeOptions({
	boxZoom: true
});

L.Map.BoxZoom = L.Handler.extend({
	initialize: function (map) {
		this._map = map;
		this._container = map._container;
		this._pane = map._panes.overlayPane;
		this._moved = false;
	},

	addHooks: function () {
		L.DomEvent.on(this._container, 'mousedown', this._onMouseDown, this);
	},

	removeHooks: function () {
		L.DomEvent.off(this._container, 'mousedown', this._onMouseDown);
		this._moved = false;
	},

	moved: function () {
		return this._moved;
	},

	_onMouseDown: function (e) {
		this._moved = false;

		if (!e.shiftKey || ((e.which !== 1) && (e.button !== 1))) { return false; }

		L.DomUtil.disableTextSelection();
		L.DomUtil.disableImageDrag();

		this._startLayerPoint = this._map.mouseEventToLayerPoint(e);

		L.DomEvent
		    .on(document, 'mousemove', this._onMouseMove, this)
		    .on(document, 'mouseup', this._onMouseUp, this)
		    .on(document, 'keydown', this._onKeyDown, this);
	},

	_onMouseMove: function (e) {
		if (!this._moved) {
			this._box = L.DomUtil.create('div', 'leaflet-zoom-box', this._pane);
			L.DomUtil.setPosition(this._box, this._startLayerPoint);

			//TODO refactor: move cursor to styles
			this._container.style.cursor = 'crosshair';
			this._map.fire('boxzoomstart');
		}

		var startPoint = this._startLayerPoint,
		    box = this._box,

		    layerPoint = this._map.mouseEventToLayerPoint(e),
		    offset = layerPoint.subtract(startPoint),

		    newPos = new L.Point(
		        Math.min(layerPoint.x, startPoint.x),
		        Math.min(layerPoint.y, startPoint.y));

		L.DomUtil.setPosition(box, newPos);

		this._moved = true;

		// TODO refactor: remove hardcoded 4 pixels
		box.style.width  = (Math.max(0, Math.abs(offset.x) - 4)) + 'px';
		box.style.height = (Math.max(0, Math.abs(offset.y) - 4)) + 'px';
	},

	_finish: function () {
		if (this._moved) {
			this._pane.removeChild(this._box);
			this._container.style.cursor = '';
		}

		L.DomUtil.enableTextSelection();
		L.DomUtil.enableImageDrag();

		L.DomEvent
		    .off(document, 'mousemove', this._onMouseMove)
		    .off(document, 'mouseup', this._onMouseUp)
		    .off(document, 'keydown', this._onKeyDown);
	},

	_onMouseUp: function (e) {

		this._finish();

		var map = this._map,
		    layerPoint = map.mouseEventToLayerPoint(e);

		if (this._startLayerPoint.equals(layerPoint)) { return; }

		var bounds = new L.LatLngBounds(
		        map.layerPointToLatLng(this._startLayerPoint),
		        map.layerPointToLatLng(layerPoint));

		map.fitBounds(bounds);

		map.fire('boxzoomend', {
			boxZoomBounds: bounds
		});
	},

	_onKeyDown: function (e) {
		if (e.keyCode === 27) {
			this._finish();
		}
	}
});

L.Map.addInitHook('addHandler', 'boxZoom', L.Map.BoxZoom);


/*
 * L.Map.Keyboard is handling keyboard interaction with the map, enabled by default.
 */

L.Map.mergeOptions({
	keyboard: true,
	keyboardPanOffset: 80,
	keyboardZoomOffset: 1
});

L.Map.Keyboard = L.Handler.extend({

	keyCodes: {
		left:    [37],
		right:   [39],
		down:    [40],
		up:      [38],
		zoomIn:  [187, 107, 61, 171],
		zoomOut: [189, 109, 173]
	},

	initialize: function (map) {
		this._map = map;

		this._setPanOffset(map.options.keyboardPanOffset);
		this._setZoomOffset(map.options.keyboardZoomOffset);
	},

	addHooks: function () {
		var container = this._map._container;

		// make the container focusable by tabbing
		if (container.tabIndex === -1) {
			container.tabIndex = '0';
		}

		L.DomEvent
		    .on(container, 'focus', this._onFocus, this)
		    .on(container, 'blur', this._onBlur, this)
		    .on(container, 'mousedown', this._onMouseDown, this);

		this._map
		    .on('focus', this._addHooks, this)
		    .on('blur', this._removeHooks, this);
	},

	removeHooks: function () {
		this._removeHooks();

		var container = this._map._container;

		L.DomEvent
		    .off(container, 'focus', this._onFocus, this)
		    .off(container, 'blur', this._onBlur, this)
		    .off(container, 'mousedown', this._onMouseDown, this);

		this._map
		    .off('focus', this._addHooks, this)
		    .off('blur', this._removeHooks, this);
	},

	_onMouseDown: function () {
		if (this._focused) { return; }

		var body = document.body,
		    docEl = document.documentElement,
		    top = body.scrollTop || docEl.scrollTop,
		    left = body.scrollLeft || docEl.scrollLeft;

		this._map._container.focus();

		window.scrollTo(left, top);
	},

	_onFocus: function () {
		this._focused = true;
		this._map.fire('focus');
	},

	_onBlur: function () {
		this._focused = false;
		this._map.fire('blur');
	},

	_setPanOffset: function (pan) {
		var keys = this._panKeys = {},
		    codes = this.keyCodes,
		    i, len;

		for (i = 0, len = codes.left.length; i < len; i++) {
			keys[codes.left[i]] = [-1 * pan, 0];
		}
		for (i = 0, len = codes.right.length; i < len; i++) {
			keys[codes.right[i]] = [pan, 0];
		}
		for (i = 0, len = codes.down.length; i < len; i++) {
			keys[codes.down[i]] = [0, pan];
		}
		for (i = 0, len = codes.up.length; i < len; i++) {
			keys[codes.up[i]] = [0, -1 * pan];
		}
	},

	_setZoomOffset: function (zoom) {
		var keys = this._zoomKeys = {},
		    codes = this.keyCodes,
		    i, len;

		for (i = 0, len = codes.zoomIn.length; i < len; i++) {
			keys[codes.zoomIn[i]] = zoom;
		}
		for (i = 0, len = codes.zoomOut.length; i < len; i++) {
			keys[codes.zoomOut[i]] = -zoom;
		}
	},

	_addHooks: function () {
		L.DomEvent.on(document, 'keydown', this._onKeyDown, this);
	},

	_removeHooks: function () {
		L.DomEvent.off(document, 'keydown', this._onKeyDown, this);
	},

	_onKeyDown: function (e) {
		var key = e.keyCode,
		    map = this._map;

		if (key in this._panKeys) {

			if (map._panAnim && map._panAnim._inProgress) { return; }

			map.panBy(this._panKeys[key]);

			if (map.options.maxBounds) {
				map.panInsideBounds(map.options.maxBounds);
			}

		} else if (key in this._zoomKeys) {
			map.setZoom(map.getZoom() + this._zoomKeys[key]);

		} else {
			return;
		}

		L.DomEvent.stop(e);
	}
});

L.Map.addInitHook('addHandler', 'keyboard', L.Map.Keyboard);


/*
 * L.Handler.MarkerDrag is used internally by L.Marker to make the markers draggable.
 */

L.Handler.MarkerDrag = L.Handler.extend({
	initialize: function (marker) {
		this._marker = marker;
	},

	addHooks: function () {
		var icon = this._marker._icon;
		if (!this._draggable) {
			this._draggable = new L.Draggable(icon, icon);
		}

		this._draggable
			.on('dragstart', this._onDragStart, this)
			.on('drag', this._onDrag, this)
			.on('dragend', this._onDragEnd, this);
		this._draggable.enable();
		L.DomUtil.addClass(this._marker._icon, 'leaflet-marker-draggable');
	},

	removeHooks: function () {
		this._draggable
			.off('dragstart', this._onDragStart, this)
			.off('drag', this._onDrag, this)
			.off('dragend', this._onDragEnd, this);

		this._draggable.disable();
		L.DomUtil.removeClass(this._marker._icon, 'leaflet-marker-draggable');
	},

	moved: function () {
		return this._draggable && this._draggable._moved;
	},

	_onDragStart: function () {
		this._marker
		    .closePopup()
		    .fire('movestart')
		    .fire('dragstart');
	},

	_onDrag: function () {
		var marker = this._marker,
		    shadow = marker._shadow,
		    iconPos = L.DomUtil.getPosition(marker._icon),
		    latlng = marker._map.layerPointToLatLng(iconPos);

		// update shadow position
		if (shadow) {
			L.DomUtil.setPosition(shadow, iconPos);
		}

		marker._latlng = latlng;

		marker
		    .fire('move', {latlng: latlng})
		    .fire('drag');
	},

	_onDragEnd: function (e) {
		this._marker
		    .fire('moveend')
		    .fire('dragend', e);
	}
});


/*
 * L.Control is a base class for implementing map controls. Handles positioning.
 * All other controls extend from this class.
 */

L.Control = L.Class.extend({
	options: {
		position: 'topright'
	},

	initialize: function (options) {
		L.setOptions(this, options);
	},

	getPosition: function () {
		return this.options.position;
	},

	setPosition: function (position) {
		var map = this._map;

		if (map) {
			map.removeControl(this);
		}

		this.options.position = position;

		if (map) {
			map.addControl(this);
		}

		return this;
	},

	getContainer: function () {
		return this._container;
	},

	addTo: function (map) {
		this._map = map;

		var container = this._container = this.onAdd(map),
		    pos = this.getPosition(),
		    corner = map._controlCorners[pos];

		L.DomUtil.addClass(container, 'leaflet-control');

		if (pos.indexOf('bottom') !== -1) {
			corner.insertBefore(container, corner.firstChild);
		} else {
			corner.appendChild(container);
		}

		return this;
	},

	removeFrom: function (map) {
		var pos = this.getPosition(),
		    corner = map._controlCorners[pos];

		corner.removeChild(this._container);
		this._map = null;

		if (this.onRemove) {
			this.onRemove(map);
		}

		return this;
	},

	_refocusOnMap: function () {
		if (this._map) {
			this._map.getContainer().focus();
		}
	}
});

L.control = function (options) {
	return new L.Control(options);
};


// adds control-related methods to L.Map

L.Map.include({
	addControl: function (control) {
		control.addTo(this);
		return this;
	},

	removeControl: function (control) {
		control.removeFrom(this);
		return this;
	},

	_initControlPos: function () {
		var corners = this._controlCorners = {},
		    l = 'leaflet-',
		    container = this._controlContainer =
		            L.DomUtil.create('div', l + 'control-container', this._container);

		function createCorner(vSide, hSide) {
			var className = l + vSide + ' ' + l + hSide;

			corners[vSide + hSide] = L.DomUtil.create('div', className, container);
		}

		createCorner('top', 'left');
		createCorner('top', 'right');
		createCorner('bottom', 'left');
		createCorner('bottom', 'right');
	},

	_clearControlPos: function () {
		this._container.removeChild(this._controlContainer);
	}
});


/*
 * L.Control.Zoom is used for the default zoom buttons on the map.
 */

L.Control.Zoom = L.Control.extend({
	options: {
		position: 'topleft',
		zoomInText: '+',
		zoomInTitle: 'Zoom in',
		zoomOutText: '-',
		zoomOutTitle: 'Zoom out'
	},

	onAdd: function (map) {
		var zoomName = 'leaflet-control-zoom',
		    container = L.DomUtil.create('div', zoomName + ' leaflet-bar');

		this._map = map;

		this._zoomInButton  = this._createButton(
		        this.options.zoomInText, this.options.zoomInTitle,
		        zoomName + '-in',  container, this._zoomIn,  this);
		this._zoomOutButton = this._createButton(
		        this.options.zoomOutText, this.options.zoomOutTitle,
		        zoomName + '-out', container, this._zoomOut, this);

		this._updateDisabled();
		map.on('zoomend zoomlevelschange', this._updateDisabled, this);

		return container;
	},

	onRemove: function (map) {
		map.off('zoomend zoomlevelschange', this._updateDisabled, this);
	},

	_zoomIn: function (e) {
		this._map.zoomIn(e.shiftKey ? 3 : 1);
	},

	_zoomOut: function (e) {
		this._map.zoomOut(e.shiftKey ? 3 : 1);
	},

	_createButton: function (html, title, className, container, fn, context) {
		var link = L.DomUtil.create('a', className, container);
		link.innerHTML = html;
		link.href = '#';
		link.title = title;

		var stop = L.DomEvent.stopPropagation;

		L.DomEvent
		    .on(link, 'click', stop)
		    .on(link, 'mousedown', stop)
		    .on(link, 'dblclick', stop)
		    .on(link, 'click', L.DomEvent.preventDefault)
		    .on(link, 'click', fn, context)
		    .on(link, 'click', this._refocusOnMap, context);

		return link;
	},

	_updateDisabled: function () {
		var map = this._map,
			className = 'leaflet-disabled';

		L.DomUtil.removeClass(this._zoomInButton, className);
		L.DomUtil.removeClass(this._zoomOutButton, className);

		if (map._zoom === map.getMinZoom()) {
			L.DomUtil.addClass(this._zoomOutButton, className);
		}
		if (map._zoom === map.getMaxZoom()) {
			L.DomUtil.addClass(this._zoomInButton, className);
		}
	}
});

L.Map.mergeOptions({
	zoomControl: true
});

L.Map.addInitHook(function () {
	if (this.options.zoomControl) {
		this.zoomControl = new L.Control.Zoom();
		this.addControl(this.zoomControl);
	}
});

L.control.zoom = function (options) {
	return new L.Control.Zoom(options);
};



/*
 * L.Control.Attribution is used for displaying attribution on the map (added by default).
 */

L.Control.Attribution = L.Control.extend({
	options: {
		position: 'bottomright',
		prefix: '<a href="http://leafletjs.com" title="A JS library for interactive maps">Leaflet</a>'
	},

	initialize: function (options) {
		L.setOptions(this, options);

		this._attributions = {};
	},

	onAdd: function (map) {
		this._container = L.DomUtil.create('div', 'leaflet-control-attribution');
		L.DomEvent.disableClickPropagation(this._container);

		for (var i in map._layers) {
			if (map._layers[i].getAttribution) {
				this.addAttribution(map._layers[i].getAttribution());
			}
		}
		
		map
		    .on('layeradd', this._onLayerAdd, this)
		    .on('layerremove', this._onLayerRemove, this);

		this._update();

		return this._container;
	},

	onRemove: function (map) {
		map
		    .off('layeradd', this._onLayerAdd)
		    .off('layerremove', this._onLayerRemove);

	},

	setPrefix: function (prefix) {
		this.options.prefix = prefix;
		this._update();
		return this;
	},

	addAttribution: function (text) {
		if (!text) { return; }

		if (!this._attributions[text]) {
			this._attributions[text] = 0;
		}
		this._attributions[text]++;

		this._update();

		return this;
	},

	removeAttribution: function (text) {
		if (!text) { return; }

		if (this._attributions[text]) {
			this._attributions[text]--;
			this._update();
		}

		return this;
	},

	_update: function () {
		if (!this._map) { return; }

		var attribs = [];

		for (var i in this._attributions) {
			if (this._attributions[i]) {
				attribs.push(i);
			}
		}

		var prefixAndAttribs = [];

		if (this.options.prefix) {
			prefixAndAttribs.push(this.options.prefix);
		}
		if (attribs.length) {
			prefixAndAttribs.push(attribs.join(', '));
		}

		this._container.innerHTML = prefixAndAttribs.join(' | ');
	},

	_onLayerAdd: function (e) {
		if (e.layer.getAttribution) {
			this.addAttribution(e.layer.getAttribution());
		}
	},

	_onLayerRemove: function (e) {
		if (e.layer.getAttribution) {
			this.removeAttribution(e.layer.getAttribution());
		}
	}
});

L.Map.mergeOptions({
	attributionControl: true
});

L.Map.addInitHook(function () {
	if (this.options.attributionControl) {
		this.attributionControl = (new L.Control.Attribution()).addTo(this);
	}
});

L.control.attribution = function (options) {
	return new L.Control.Attribution(options);
};


/*
 * L.Control.Scale is used for displaying metric/imperial scale on the map.
 */

L.Control.Scale = L.Control.extend({
	options: {
		position: 'bottomleft',
		maxWidth: 100,
		metric: true,
		imperial: true,
		updateWhenIdle: false
	},

	onAdd: function (map) {
		this._map = map;

		var className = 'leaflet-control-scale',
		    container = L.DomUtil.create('div', className),
		    options = this.options;

		this._addScales(options, className, container);

		map.on(options.updateWhenIdle ? 'moveend' : 'move', this._update, this);
		map.whenReady(this._update, this);

		return container;
	},

	onRemove: function (map) {
		map.off(this.options.updateWhenIdle ? 'moveend' : 'move', this._update, this);
	},

	_addScales: function (options, className, container) {
		if (options.metric) {
			this._mScale = L.DomUtil.create('div', className + '-line', container);
		}
		if (options.imperial) {
			this._iScale = L.DomUtil.create('div', className + '-line', container);
		}
	},

	_update: function () {
		var bounds = this._map.getBounds(),
		    centerLat = bounds.getCenter().lat,
		    halfWorldMeters = 6378137 * Math.PI * Math.cos(centerLat * Math.PI / 180),
		    dist = halfWorldMeters * (bounds.getNorthEast().lng - bounds.getSouthWest().lng) / 180,

		    size = this._map.getSize(),
		    options = this.options,
		    maxMeters = 0;

		if (size.x > 0) {
			maxMeters = dist * (options.maxWidth / size.x);
		}

		this._updateScales(options, maxMeters);
	},

	_updateScales: function (options, maxMeters) {
		if (options.metric && maxMeters) {
			this._updateMetric(maxMeters);
		}

		if (options.imperial && maxMeters) {
			this._updateImperial(maxMeters);
		}
	},

	_updateMetric: function (maxMeters) {
		var meters = this._getRoundNum(maxMeters);

		this._mScale.style.width = this._getScaleWidth(meters / maxMeters) + 'px';
		this._mScale.innerHTML = meters < 1000 ? meters + ' m' : (meters / 1000) + ' km';
	},

	_updateImperial: function (maxMeters) {
		var maxFeet = maxMeters * 3.2808399,
		    scale = this._iScale,
		    maxMiles, miles, feet;

		if (maxFeet > 5280) {
			maxMiles = maxFeet / 5280;
			miles = this._getRoundNum(maxMiles);

			scale.style.width = this._getScaleWidth(miles / maxMiles) + 'px';
			scale.innerHTML = miles + ' mi';

		} else {
			feet = this._getRoundNum(maxFeet);

			scale.style.width = this._getScaleWidth(feet / maxFeet) + 'px';
			scale.innerHTML = feet + ' ft';
		}
	},

	_getScaleWidth: function (ratio) {
		return Math.round(this.options.maxWidth * ratio) - 10;
	},

	_getRoundNum: function (num) {
		var pow10 = Math.pow(10, (Math.floor(num) + '').length - 1),
		    d = num / pow10;

		d = d >= 10 ? 10 : d >= 5 ? 5 : d >= 3 ? 3 : d >= 2 ? 2 : 1;

		return pow10 * d;
	}
});

L.control.scale = function (options) {
	return new L.Control.Scale(options);
};


/*
 * L.Control.Layers is a control to allow users to switch between different layers on the map.
 */

L.Control.Layers = L.Control.extend({
	options: {
		collapsed: true,
		position: 'topright',
		autoZIndex: true
	},

	initialize: function (baseLayers, overlays, options) {
		L.setOptions(this, options);

		this._layers = {};
		this._lastZIndex = 0;
		this._handlingClick = false;

		for (var i in baseLayers) {
			this._addLayer(baseLayers[i], i);
		}

		for (i in overlays) {
			this._addLayer(overlays[i], i, true);
		}
	},

	onAdd: function (map) {
		this._initLayout();
		this._update();

		map
		    .on('layeradd', this._onLayerChange, this)
		    .on('layerremove', this._onLayerChange, this);

		return this._container;
	},

	onRemove: function (map) {
		map
		    .off('layeradd', this._onLayerChange, this)
		    .off('layerremove', this._onLayerChange, this);
	},

	addBaseLayer: function (layer, name) {
		this._addLayer(layer, name);
		this._update();
		return this;
	},

	addOverlay: function (layer, name) {
		this._addLayer(layer, name, true);
		this._update();
		return this;
	},

	removeLayer: function (layer) {
		var id = L.stamp(layer);
		delete this._layers[id];
		this._update();
		return this;
	},

	_initLayout: function () {
		var className = 'leaflet-control-layers',
		    container = this._container = L.DomUtil.create('div', className);

		//Makes this work on IE10 Touch devices by stopping it from firing a mouseout event when the touch is released
		container.setAttribute('aria-haspopup', true);

		if (!L.Browser.touch) {
			L.DomEvent
				.disableClickPropagation(container)
				.disableScrollPropagation(container);
		} else {
			L.DomEvent.on(container, 'click', L.DomEvent.stopPropagation);
		}

		var form = this._form = L.DomUtil.create('form', className + '-list');

		if (this.options.collapsed) {
			if (!L.Browser.android) {
				L.DomEvent
				    .on(container, 'mouseover', this._expand, this)
				    .on(container, 'mouseout', this._collapse, this);
			}
			var link = this._layersLink = L.DomUtil.create('a', className + '-toggle', container);
			link.href = '#';
			link.title = 'Layers';

			if (L.Browser.touch) {
				L.DomEvent
				    .on(link, 'click', L.DomEvent.stop)
				    .on(link, 'click', this._expand, this);
			}
			else {
				L.DomEvent.on(link, 'focus', this._expand, this);
			}
			//Work around for Firefox android issue https://github.com/Leaflet/Leaflet/issues/2033
			L.DomEvent.on(form, 'click', function () {
				setTimeout(L.bind(this._onInputClick, this), 0);
			}, this);

			this._map.on('click', this._collapse, this);
			// TODO keyboard accessibility
		} else {
			this._expand();
		}

		this._baseLayersList = L.DomUtil.create('div', className + '-base', form);
		this._separator = L.DomUtil.create('div', className + '-separator', form);
		this._overlaysList = L.DomUtil.create('div', className + '-overlays', form);

		container.appendChild(form);
	},

	_addLayer: function (layer, name, overlay) {
		var id = L.stamp(layer);

		this._layers[id] = {
			layer: layer,
			name: name,
			overlay: overlay
		};

		if (this.options.autoZIndex && layer.setZIndex) {
			this._lastZIndex++;
			layer.setZIndex(this._lastZIndex);
		}
	},

	_update: function () {
		if (!this._container) {
			return;
		}

		this._baseLayersList.innerHTML = '';
		this._overlaysList.innerHTML = '';

		var baseLayersPresent = false,
		    overlaysPresent = false,
		    i, obj;

		for (i in this._layers) {
			obj = this._layers[i];
			this._addItem(obj);
			overlaysPresent = overlaysPresent || obj.overlay;
			baseLayersPresent = baseLayersPresent || !obj.overlay;
		}

		this._separator.style.display = overlaysPresent && baseLayersPresent ? '' : 'none';
	},

	_onLayerChange: function (e) {
		var obj = this._layers[L.stamp(e.layer)];

		if (!obj) { return; }

		if (!this._handlingClick) {
			this._update();
		}

		var type = obj.overlay ?
			(e.type === 'layeradd' ? 'overlayadd' : 'overlayremove') :
			(e.type === 'layeradd' ? 'baselayerchange' : null);

		if (type) {
			this._map.fire(type, obj);
		}
	},

	// IE7 bugs out if you create a radio dynamically, so you have to do it this hacky way (see http://bit.ly/PqYLBe)
	_createRadioElement: function (name, checked) {

		var radioHtml = '<input type="radio" class="leaflet-control-layers-selector" name="' + name + '"';
		if (checked) {
			radioHtml += ' checked="checked"';
		}
		radioHtml += '/>';

		var radioFragment = document.createElement('div');
		radioFragment.innerHTML = radioHtml;

		return radioFragment.firstChild;
	},

	_addItem: function (obj) {
		var label = document.createElement('label'),
		    input,
		    checked = this._map.hasLayer(obj.layer);

		if (obj.overlay) {
			input = document.createElement('input');
			input.type = 'checkbox';
			input.className = 'leaflet-control-layers-selector';
			input.defaultChecked = checked;
		} else {
			input = this._createRadioElement('leaflet-base-layers', checked);
		}

		input.layerId = L.stamp(obj.layer);

		L.DomEvent.on(input, 'click', this._onInputClick, this);

		var name = document.createElement('span');
		name.innerHTML = ' ' + obj.name;

		label.appendChild(input);
		label.appendChild(name);

		var container = obj.overlay ? this._overlaysList : this._baseLayersList;
		container.appendChild(label);

		return label;
	},

	_onInputClick: function () {
		var i, input, obj,
		    inputs = this._form.getElementsByTagName('input'),
		    inputsLen = inputs.length;

		this._handlingClick = true;

		for (i = 0; i < inputsLen; i++) {
			input = inputs[i];
			obj = this._layers[input.layerId];

			if (input.checked && !this._map.hasLayer(obj.layer)) {
				this._map.addLayer(obj.layer);

			} else if (!input.checked && this._map.hasLayer(obj.layer)) {
				this._map.removeLayer(obj.layer);
			}
		}

		this._handlingClick = false;

		this._refocusOnMap();
	},

	_expand: function () {
		L.DomUtil.addClass(this._container, 'leaflet-control-layers-expanded');
	},

	_collapse: function () {
		this._container.className = this._container.className.replace(' leaflet-control-layers-expanded', '');
	}
});

L.control.layers = function (baseLayers, overlays, options) {
	return new L.Control.Layers(baseLayers, overlays, options);
};


/*
 * L.PosAnimation is used by Leaflet internally for pan animations.
 */

L.PosAnimation = L.Class.extend({
	includes: L.Mixin.Events,

	run: function (el, newPos, duration, easeLinearity) { // (HTMLElement, Point[, Number, Number])
		this.stop();

		this._el = el;
		this._inProgress = true;
		this._newPos = newPos;

		this.fire('start');

		el.style[L.DomUtil.TRANSITION] = 'all ' + (duration || 0.25) +
		        's cubic-bezier(0,0,' + (easeLinearity || 0.5) + ',1)';

		L.DomEvent.on(el, L.DomUtil.TRANSITION_END, this._onTransitionEnd, this);
		L.DomUtil.setPosition(el, newPos);

		// toggle reflow, Chrome flickers for some reason if you don't do this
		L.Util.falseFn(el.offsetWidth);

		// there's no native way to track value updates of transitioned properties, so we imitate this
		this._stepTimer = setInterval(L.bind(this._onStep, this), 50);
	},

	stop: function () {
		if (!this._inProgress) { return; }

		// if we just removed the transition property, the element would jump to its final position,
		// so we need to make it stay at the current position

		L.DomUtil.setPosition(this._el, this._getPos());
		this._onTransitionEnd();
		L.Util.falseFn(this._el.offsetWidth); // force reflow in case we are about to start a new animation
	},

	_onStep: function () {
		var stepPos = this._getPos();
		if (!stepPos) {
			this._onTransitionEnd();
			return;
		}
		// jshint camelcase: false
		// make L.DomUtil.getPosition return intermediate position value during animation
		this._el._leaflet_pos = stepPos;

		this.fire('step');
	},

	// you can't easily get intermediate values of properties animated with CSS3 Transitions,
	// we need to parse computed style (in case of transform it returns matrix string)

	_transformRe: /([-+]?(?:\d*\.)?\d+)\D*, ([-+]?(?:\d*\.)?\d+)\D*\)/,

	_getPos: function () {
		var left, top, matches,
		    el = this._el,
		    style = window.getComputedStyle(el);

		if (L.Browser.any3d) {
			matches = style[L.DomUtil.TRANSFORM].match(this._transformRe);
			if (!matches) { return; }
			left = parseFloat(matches[1]);
			top  = parseFloat(matches[2]);
		} else {
			left = parseFloat(style.left);
			top  = parseFloat(style.top);
		}

		return new L.Point(left, top, true);
	},

	_onTransitionEnd: function () {
		L.DomEvent.off(this._el, L.DomUtil.TRANSITION_END, this._onTransitionEnd, this);

		if (!this._inProgress) { return; }
		this._inProgress = false;

		this._el.style[L.DomUtil.TRANSITION] = '';

		// jshint camelcase: false
		// make sure L.DomUtil.getPosition returns the final position value after animation
		this._el._leaflet_pos = this._newPos;

		clearInterval(this._stepTimer);

		this.fire('step').fire('end');
	}

});


/*
 * Extends L.Map to handle panning animations.
 */

L.Map.include({

	setView: function (center, zoom, options) {

		zoom = zoom === undefined ? this._zoom : this._limitZoom(zoom);
		center = this._limitCenter(L.latLng(center), zoom, this.options.maxBounds);
		options = options || {};

		if (this._panAnim) {
			this._panAnim.stop();
		}

		if (this._loaded && !options.reset && options !== true) {

			if (options.animate !== undefined) {
				options.zoom = L.extend({animate: options.animate}, options.zoom);
				options.pan = L.extend({animate: options.animate}, options.pan);
			}

			// try animating pan or zoom
			var animated = (this._zoom !== zoom) ?
				this._tryAnimatedZoom && this._tryAnimatedZoom(center, zoom, options.zoom) :
				this._tryAnimatedPan(center, options.pan);

			if (animated) {
				// prevent resize handler call, the view will refresh after animation anyway
				clearTimeout(this._sizeTimer);
				return this;
			}
		}

		// animation didn't start, just reset the map view
		this._resetView(center, zoom);

		return this;
	},

	panBy: function (offset, options) {
		offset = L.point(offset).round();
		options = options || {};

		if (!offset.x && !offset.y) {
			return this;
		}

		if (!this._panAnim) {
			this._panAnim = new L.PosAnimation();

			this._panAnim.on({
				'step': this._onPanTransitionStep,
				'end': this._onPanTransitionEnd
			}, this);
		}

		// don't fire movestart if animating inertia
		if (!options.noMoveStart) {
			this.fire('movestart');
		}

		// animate pan unless animate: false specified
		if (options.animate !== false) {
			L.DomUtil.addClass(this._mapPane, 'leaflet-pan-anim');

			var newPos = this._getMapPanePos().subtract(offset);
			this._panAnim.run(this._mapPane, newPos, options.duration || 0.25, options.easeLinearity);
		} else {
			this._rawPanBy(offset);
			this.fire('move').fire('moveend');
		}

		return this;
	},

	_onPanTransitionStep: function () {
		this.fire('move');
	},

	_onPanTransitionEnd: function () {
		L.DomUtil.removeClass(this._mapPane, 'leaflet-pan-anim');
		this.fire('moveend');
	},

	_tryAnimatedPan: function (center, options) {
		// difference between the new and current centers in pixels
		var offset = this._getCenterOffset(center)._floor();

		// don't animate too far unless animate: true specified in options
		if ((options && options.animate) !== true && !this.getSize().contains(offset)) { return false; }

		this.panBy(offset, options);

		return true;
	}
});


/*
 * L.PosAnimation fallback implementation that powers Leaflet pan animations
 * in browsers that don't support CSS3 Transitions.
 */

L.PosAnimation = L.DomUtil.TRANSITION ? L.PosAnimation : L.PosAnimation.extend({

	run: function (el, newPos, duration, easeLinearity) { // (HTMLElement, Point[, Number, Number])
		this.stop();

		this._el = el;
		this._inProgress = true;
		this._duration = duration || 0.25;
		this._easeOutPower = 1 / Math.max(easeLinearity || 0.5, 0.2);

		this._startPos = L.DomUtil.getPosition(el);
		this._offset = newPos.subtract(this._startPos);
		this._startTime = +new Date();

		this.fire('start');

		this._animate();
	},

	stop: function () {
		if (!this._inProgress) { return; }

		this._step();
		this._complete();
	},

	_animate: function () {
		// animation loop
		this._animId = L.Util.requestAnimFrame(this._animate, this);
		this._step();
	},

	_step: function () {
		var elapsed = (+new Date()) - this._startTime,
		    duration = this._duration * 1000;

		if (elapsed < duration) {
			this._runFrame(this._easeOut(elapsed / duration));
		} else {
			this._runFrame(1);
			this._complete();
		}
	},

	_runFrame: function (progress) {
		var pos = this._startPos.add(this._offset.multiplyBy(progress));
		L.DomUtil.setPosition(this._el, pos);

		this.fire('step');
	},

	_complete: function () {
		L.Util.cancelAnimFrame(this._animId);

		this._inProgress = false;
		this.fire('end');
	},

	_easeOut: function (t) {
		return 1 - Math.pow(1 - t, this._easeOutPower);
	}
});


/*
 * Extends L.Map to handle zoom animations.
 */

L.Map.mergeOptions({
	zoomAnimation: true,
	zoomAnimationThreshold: 4
});

if (L.DomUtil.TRANSITION) {

	L.Map.addInitHook(function () {
		// don't animate on browsers without hardware-accelerated transitions or old Android/Opera
		this._zoomAnimated = this.options.zoomAnimation && L.DomUtil.TRANSITION &&
				L.Browser.any3d && !L.Browser.android23 && !L.Browser.mobileOpera;

		// zoom transitions run with the same duration for all layers, so if one of transitionend events
		// happens after starting zoom animation (propagating to the map pane), we know that it ended globally
		if (this._zoomAnimated) {
			L.DomEvent.on(this._mapPane, L.DomUtil.TRANSITION_END, this._catchTransitionEnd, this);
		}
	});
}

L.Map.include(!L.DomUtil.TRANSITION ? {} : {

	_catchTransitionEnd: function (e) {
		if (this._animatingZoom && e.propertyName.indexOf('transform') >= 0) {
			this._onZoomTransitionEnd();
		}
	},

	_nothingToAnimate: function () {
		return !this._container.getElementsByClassName('leaflet-zoom-animated').length;
	},

	_tryAnimatedZoom: function (center, zoom, options) {

		if (this._animatingZoom) { return true; }

		options = options || {};

		// don't animate if disabled, not supported or zoom difference is too large
		if (!this._zoomAnimated || options.animate === false || this._nothingToAnimate() ||
		        Math.abs(zoom - this._zoom) > this.options.zoomAnimationThreshold) { return false; }

		// offset is the pixel coords of the zoom origin relative to the current center
		var scale = this.getZoomScale(zoom),
		    offset = this._getCenterOffset(center)._divideBy(1 - 1 / scale),
			origin = this._getCenterLayerPoint()._add(offset);

		// don't animate if the zoom origin isn't within one screen from the current center, unless forced
		if (options.animate !== true && !this.getSize().contains(offset)) { return false; }

		this
		    .fire('movestart')
		    .fire('zoomstart');

		this._animateZoom(center, zoom, origin, scale, null, true);

		return true;
	},

	_animateZoom: function (center, zoom, origin, scale, delta, backwards, forTouchZoom) {

		if (!forTouchZoom) {
			this._animatingZoom = true;
		}

		// put transform transition on all layers with leaflet-zoom-animated class
		L.DomUtil.addClass(this._mapPane, 'leaflet-zoom-anim');

		// remember what center/zoom to set after animation
		this._animateToCenter = center;
		this._animateToZoom = zoom;

		// disable any dragging during animation
		if (L.Draggable) {
			L.Draggable._disabled = true;
		}

		L.Util.requestAnimFrame(function () {
			this.fire('zoomanim', {
				center: center,
				zoom: zoom,
				origin: origin,
				scale: scale,
				delta: delta,
				backwards: backwards
			});
			// horrible hack to work around a Chrome bug https://github.com/Leaflet/Leaflet/issues/3689
			setTimeout(L.bind(this._onZoomTransitionEnd, this), 250);
		}, this);
	},

	_onZoomTransitionEnd: function () {
		if (!this._animatingZoom) { return; }

		this._animatingZoom = false;

		L.DomUtil.removeClass(this._mapPane, 'leaflet-zoom-anim');

		L.Util.requestAnimFrame(function () {
			this._resetView(this._animateToCenter, this._animateToZoom, true, true);

			if (L.Draggable) {
				L.Draggable._disabled = false;
			}
		}, this);
	}
});


/*
	Zoom animation logic for L.TileLayer.
*/

L.TileLayer.include({
	_animateZoom: function (e) {
		if (!this._animating) {
			this._animating = true;
			this._prepareBgBuffer();
		}

		var bg = this._bgBuffer,
		    transform = L.DomUtil.TRANSFORM,
		    initialTransform = e.delta ? L.DomUtil.getTranslateString(e.delta) : bg.style[transform],
		    scaleStr = L.DomUtil.getScaleString(e.scale, e.origin);

		bg.style[transform] = e.backwards ?
				scaleStr + ' ' + initialTransform :
				initialTransform + ' ' + scaleStr;
	},

	_endZoomAnim: function () {
		var front = this._tileContainer,
		    bg = this._bgBuffer;

		front.style.visibility = '';
		front.parentNode.appendChild(front); // Bring to fore

		// force reflow
		L.Util.falseFn(bg.offsetWidth);

		var zoom = this._map.getZoom();
		if (zoom > this.options.maxZoom || zoom < this.options.minZoom) {
			this._clearBgBuffer();
		}

		this._animating = false;
	},

	_clearBgBuffer: function () {
		var map = this._map;

		if (map && !map._animatingZoom && !map.touchZoom._zooming) {
			this._bgBuffer.innerHTML = '';
			this._bgBuffer.style[L.DomUtil.TRANSFORM] = '';
		}
	},

	_prepareBgBuffer: function () {

		var front = this._tileContainer,
		    bg = this._bgBuffer;

		// if foreground layer doesn't have many tiles but bg layer does,
		// keep the existing bg layer and just zoom it some more

		var bgLoaded = this._getLoadedTilesPercentage(bg),
		    frontLoaded = this._getLoadedTilesPercentage(front);

		if (bg && bgLoaded > 0.5 && frontLoaded < 0.5) {

			front.style.visibility = 'hidden';
			this._stopLoadingImages(front);
			return;
		}

		// prepare the buffer to become the front tile pane
		bg.style.visibility = 'hidden';
		bg.style[L.DomUtil.TRANSFORM] = '';

		// switch out the current layer to be the new bg layer (and vice-versa)
		this._tileContainer = bg;
		bg = this._bgBuffer = front;

		this._stopLoadingImages(bg);

		//prevent bg buffer from clearing right after zoom
		clearTimeout(this._clearBgBufferTimer);
	},

	_getLoadedTilesPercentage: function (container) {
		var tiles = container.getElementsByTagName('img'),
		    i, len, count = 0;

		for (i = 0, len = tiles.length; i < len; i++) {
			if (tiles[i].complete) {
				count++;
			}
		}
		return count / len;
	},

	// stops loading all tiles in the background layer
	_stopLoadingImages: function (container) {
		var tiles = Array.prototype.slice.call(container.getElementsByTagName('img')),
		    i, len, tile;

		for (i = 0, len = tiles.length; i < len; i++) {
			tile = tiles[i];

			if (!tile.complete) {
				tile.onload = L.Util.falseFn;
				tile.onerror = L.Util.falseFn;
				tile.src = L.Util.emptyImageUrl;

				tile.parentNode.removeChild(tile);
			}
		}
	}
});


/*
 * Provides L.Map with convenient shortcuts for using browser geolocation features.
 */

L.Map.include({
	_defaultLocateOptions: {
		watch: false,
		setView: false,
		maxZoom: Infinity,
		timeout: 10000,
		maximumAge: 0,
		enableHighAccuracy: false
	},

	locate: function (/*Object*/ options) {

		options = this._locateOptions = L.extend(this._defaultLocateOptions, options);

		if (!navigator.geolocation) {
			this._handleGeolocationError({
				code: 0,
				message: 'Geolocation not supported.'
			});
			return this;
		}

		var onResponse = L.bind(this._handleGeolocationResponse, this),
			onError = L.bind(this._handleGeolocationError, this);

		if (options.watch) {
			this._locationWatchId =
			        navigator.geolocation.watchPosition(onResponse, onError, options);
		} else {
			navigator.geolocation.getCurrentPosition(onResponse, onError, options);
		}
		return this;
	},

	stopLocate: function () {
		if (navigator.geolocation) {
			navigator.geolocation.clearWatch(this._locationWatchId);
		}
		if (this._locateOptions) {
			this._locateOptions.setView = false;
		}
		return this;
	},

	_handleGeolocationError: function (error) {
		var c = error.code,
		    message = error.message ||
		            (c === 1 ? 'permission denied' :
		            (c === 2 ? 'position unavailable' : 'timeout'));

		if (this._locateOptions.setView && !this._loaded) {
			this.fitWorld();
		}

		this.fire('locationerror', {
			code: c,
			message: 'Geolocation error: ' + message + '.'
		});
	},

	_handleGeolocationResponse: function (pos) {
		var lat = pos.coords.latitude,
		    lng = pos.coords.longitude,
		    latlng = new L.LatLng(lat, lng),

		    latAccuracy = 180 * pos.coords.accuracy / 40075017,
		    lngAccuracy = latAccuracy / Math.cos(L.LatLng.DEG_TO_RAD * lat),

		    bounds = L.latLngBounds(
		            [lat - latAccuracy, lng - lngAccuracy],
		            [lat + latAccuracy, lng + lngAccuracy]),

		    options = this._locateOptions;

		if (options.setView) {
			var zoom = Math.min(this.getBoundsZoom(bounds), options.maxZoom);
			this.setView(latlng, zoom);
		}

		var data = {
			latlng: latlng,
			bounds: bounds,
			timestamp: pos.timestamp
		};

		for (var i in pos.coords) {
			if (typeof pos.coords[i] === 'number') {
				data[i] = pos.coords[i];
			}
		}

		this.fire('locationfound', data);
	}
});


}(window, document));

L.Control.Fullscreen = L.Control.extend({
    options: {
        position: 'topleft',
        title: {
            'false': 'View Fullscreen',
            'true': 'Exit Fullscreen'
        }
    },

    onAdd: function (map) {
        var container = L.DomUtil.create('div', 'leaflet-control-fullscreen leaflet-bar leaflet-control');

        this.link = L.DomUtil.create('a', 'leaflet-control-fullscreen-button leaflet-bar-part', container);
        this.link.href = '#';

        this._map = map;
        this._map.on('fullscreenchange', this._toggleTitle, this);
        this._toggleTitle();

        L.DomEvent.on(this.link, 'click', this._click, this);

        return container;
    },

    _click: function (e) {
        L.DomEvent.stopPropagation(e);
        L.DomEvent.preventDefault(e);
        this._map.toggleFullscreen();
    },

    _toggleTitle: function() {
        this.link.title = this.options.title[this._map.isFullscreen()];
    }
});

L.Map.include({
    isFullscreen: function () {
        return this._isFullscreen || false;
    },

    toggleFullscreen: function () {
        var container = this.getContainer();
        if (this.isFullscreen()) {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.webkitCancelFullScreen) {
                document.webkitCancelFullScreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            } else {
                L.DomUtil.removeClass(container, 'leaflet-pseudo-fullscreen');
                this._setFullscreen(false);
                this.invalidateSize();
                this.fire('fullscreenchange');
            }
        } else {
            if (container.requestFullscreen) {
                container.requestFullscreen();
            } else if (container.mozRequestFullScreen) {
                container.mozRequestFullScreen();
            } else if (container.webkitRequestFullscreen) {
                container.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
            } else if (container.msRequestFullscreen) {
                container.msRequestFullscreen();
            } else {
                L.DomUtil.addClass(container, 'leaflet-pseudo-fullscreen');
                this._setFullscreen(true);
                this.invalidateSize();
                this.fire('fullscreenchange');
            }
        }
    },

    _setFullscreen: function(fullscreen) {
        this._isFullscreen = fullscreen;
        var container = this.getContainer();
        if (fullscreen) {
            L.DomUtil.addClass(container, 'leaflet-fullscreen-on');
        } else {
            L.DomUtil.removeClass(container, 'leaflet-fullscreen-on');
        }
    },

    _onFullscreenChange: function (e) {
        var fullscreenElement =
            document.fullscreenElement ||
            document.mozFullScreenElement ||
            document.webkitFullscreenElement ||
            document.msFullscreenElement;

        if (fullscreenElement === this.getContainer() && !this._isFullscreen) {
            this._setFullscreen(true);
            this.fire('fullscreenchange');
        } else if (fullscreenElement !== this.getContainer() && this._isFullscreen) {
            this._setFullscreen(false);
            this.fire('fullscreenchange');
        }
    }
});

L.Map.mergeOptions({
    fullscreenControl: false
});

L.Map.addInitHook(function () {
    if (this.options.fullscreenControl) {
        this.fullscreenControl = new L.Control.Fullscreen();
        this.addControl(this.fullscreenControl);
    }

    var fullscreenchange;

    if ('onfullscreenchange' in document) {
        fullscreenchange = 'fullscreenchange';
    } else if ('onmozfullscreenchange' in document) {
        fullscreenchange = 'mozfullscreenchange';
    } else if ('onwebkitfullscreenchange' in document) {
        fullscreenchange = 'webkitfullscreenchange';
    } else if ('onmsfullscreenchange' in document) {
        fullscreenchange = 'MSFullscreenChange';
    }

    if (fullscreenchange) {
        var onFullscreenChange = L.bind(this._onFullscreenChange, this);

        this.whenReady(function () {
            L.DomEvent.on(document, fullscreenchange, onFullscreenChange);
        });

        this.on('unload', function () {
            L.DomEvent.off(document, fullscreenchange, onFullscreenChange);
        });
    }
});

L.control.fullscreen = function (options) {
    return new L.Control.Fullscreen(options);
};


(function (root, factory) {
	// Assume Leaflet is loaded into global object L already
	factory(L);
}(this, function (L) {
	'use strict';

	L.TileLayer.Provider = L.TileLayer.extend({
		initialize: function (arg, options) {
			var providers = L.TileLayer.Provider.providers;

			var parts = arg.split('.');

			var providerName = parts[0];
			var variantName = parts[1];

			if (!providers[providerName]) {
				throw 'No such provider (' + providerName + ')';
			}

			var provider = {
				url: providers[providerName].url,
				options: providers[providerName].options
			};

			// overwrite values in provider from variant.
			if (variantName && 'variants' in providers[providerName]) {
				if (!(variantName in providers[providerName].variants)) {
					throw 'No such variant of ' + providerName + ' (' + variantName + ')';
				}
				var variant = providers[providerName].variants[variantName];
				var variantOptions;
				if (typeof variant === 'string') {
					variantOptions = {
						variant: variant
					};
				} else {
					variantOptions = variant.options;
				}
				provider = {
					url: variant.url || provider.url,
					options: L.Util.extend({}, provider.options, variantOptions)
				};
			} else if (typeof provider.url === 'function') {
				provider.url = provider.url(parts.splice(1, parts.length - 1).join('.'));
			}

			var forceHTTP = window.location.protocol === 'file:' || provider.options.forceHTTP;
			if (provider.url.indexOf('//') === 0 && forceHTTP) {
				provider.url = 'http:' + provider.url;
			}

			// If retina option is set
			if (provider.options.retina) {
				// Check retina screen
				if (options.detectRetina && L.Browser.retina) {
					// The retina option will be active now
					// But we need to prevent Leaflet retina mode
					options.detectRetina = false;
				} else {
					// No retina, remove option
					provider.options.retina = '';
				}
			}

			// replace attribution placeholders with their values from toplevel provider attribution,
			// recursively
			var attributionReplacer = function (attr) {
				if (attr.indexOf('{attribution.') === -1) {
					return attr;
				}
				return attr.replace(/\{attribution.(\w*)\}/,
					function (match, attributionName) {
						return attributionReplacer(providers[attributionName].options.attribution);
					}
				);
			};
			provider.options.attribution = attributionReplacer(provider.options.attribution);

			// Compute final options combining provider options with any user overrides
			var layerOpts = L.Util.extend({}, provider.options, options);
			L.TileLayer.prototype.initialize.call(this, provider.url, layerOpts);
		}
	});

	/**
	 * Definition of providers.
	 * see http://leafletjs.com/reference.html#tilelayer for options in the options map.
	 */

	L.TileLayer.Provider.providers = {
		OpenStreetMap: {
			url: '//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
			options: {
				maxZoom: 19,
				attribution:
					'&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
			},
			variants: {
				Mapnik: {},
				BlackAndWhite: {
					url: 'http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png',
					options: {
						maxZoom: 18
					}
				},
				DE: {
					url: 'http://{s}.tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png',
					options: {
						maxZoom: 18
					}
				},
				France: {
					url: 'http://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png',
					options: {
						attribution: '&copy; Openstreetmap France | {attribution.OpenStreetMap}'
					}
				},
				HOT: {
					url: 'http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
					options: {
						attribution: '{attribution.OpenStreetMap}, Tiles courtesy of <a href="http://hot.openstreetmap.org/" target="_blank">Humanitarian OpenStreetMap Team</a>'
					}
				}
			}
		},
		OpenSeaMap: {
			url: 'http://tiles.openseamap.org/seamark/{z}/{x}/{y}.png',
			options: {
				attribution: 'Map data: &copy; <a href="http://www.openseamap.org">OpenSeaMap</a> contributors'
			}
		},
		OpenTopoMap: {
			url: '//{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
			options: {
				maxZoom: 16,
				attribution: 'Map data: {attribution.OpenStreetMap}, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
			}
		},
		Thunderforest: {
			url: '//{s}.tile.thunderforest.com/{variant}/{z}/{x}/{y}.png',
			options: {
				attribution:
					'&copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>, {attribution.OpenStreetMap}',
				variant: 'cycle'
			},
			variants: {
				OpenCycleMap: 'cycle',
				Transport: {
					options: {
						variant: 'transport',
						maxZoom: 19
					}
				},
				TransportDark: {
					options: {
						variant: 'transport-dark',
						maxZoom: 19
					}
				},
				Landscape: 'landscape',
				Outdoors: 'outdoors'
			}
		},
		OpenMapSurfer: {
			url: 'http://openmapsurfer.uni-hd.de/tiles/{variant}/x={x}&y={y}&z={z}',
			options: {
				maxZoom: 20,
				variant: 'roads',
				attribution: 'Imagery from <a href="http://giscience.uni-hd.de/">GIScience Research Group @ University of Heidelberg</a> &mdash; Map data {attribution.OpenStreetMap}'
			},
			variants: {
				Roads: 'roads',
				AdminBounds: {
					options: {
						variant: 'adminb',
						maxZoom: 19
					}
				},
				Grayscale: {
					options: {
						variant: 'roadsg',
						maxZoom: 19
					}
				}
			}
		},
		Hydda: {
			url: 'http://{s}.tile.openstreetmap.se/hydda/{variant}/{z}/{x}/{y}.png',
			options: {
				variant: 'full',
				attribution: 'Tiles courtesy of <a href="http://openstreetmap.se/" target="_blank">OpenStreetMap Sweden</a> &mdash; Map data {attribution.OpenStreetMap}'
			},
			variants: {
				Full: 'full',
				Base: 'base',
				RoadsAndLabels: 'roads_and_labels'
			}
		},
		MapQuestOpen: {
			/* Mapquest does support https, but with a different subdomain:
			 * https://otile{s}-s.mqcdn.com/tiles/1.0.0/{type}/{z}/{x}/{y}.{ext}
			 * which makes implementing protocol relativity impossible.
			 */
			url: 'http://otile{s}.mqcdn.com/tiles/1.0.0/{type}/{z}/{x}/{y}.{ext}',
			options: {
				type: 'map',
				ext: 'jpg',
				attribution:
					'Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash; ' +
					'Map data {attribution.OpenStreetMap}',
				subdomains: '1234'
			},
			variants: {
				OSM: {},
				Aerial: {
					options: {
						type: 'sat',
						attribution:
							'Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash; ' +
							'Portions Courtesy NASA/JPL-Caltech and U.S. Depart. of Agriculture, Farm Service Agency'
					}
				},
				HybridOverlay: {
					options: {
						type: 'hyb',
						ext: 'png',
						opacity: 0.9
					}
				}
			}
		},
		MapBox: {
			url: '//api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}',
			options: {
				attribution:
					'Imagery from <a href="http://mapbox.com/about/maps/">MapBox</a> &mdash; ' +
					'Map data {attribution.OpenStreetMap}',
				subdomains: 'abcd'
			}
		},
		Stamen: {
			url: '//stamen-tiles-{s}.a.ssl.fastly.net/{variant}/{z}/{x}/{y}.{ext}',
			options: {
				attribution:
					'Map tiles by <a href="http://stamen.com">Stamen Design</a>, ' +
					'<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; ' +
					'Map data {attribution.OpenStreetMap}',
				subdomains: 'abcd',
				minZoom: 0,
				maxZoom: 20,
				variant: 'toner',
				ext: 'png'
			},
			variants: {
				Toner: 'toner',
				TonerBackground: 'toner-background',
				TonerHybrid: 'toner-hybrid',
				TonerLines: 'toner-lines',
				TonerLabels: 'toner-labels',
				TonerLite: 'toner-lite',
				Watercolor: {
					options: {
						variant: 'watercolor',
						minZoom: 1,
						maxZoom: 16
					}
				},
				Terrain: {
					options: {
						variant: 'terrain',
						minZoom: 4,
						maxZoom: 18,
						bounds: [[22, -132], [70, -56]]
					}
				},
				TerrainBackground: {
					options: {
						variant: 'terrain-background',
						minZoom: 4,
						maxZoom: 18,
						bounds: [[22, -132], [70, -56]]
					}
				},
				TopOSMRelief: {
					options: {
						variant: 'toposm-color-relief',
						ext: 'jpg',
						bounds: [[22, -132], [51, -56]]
					}
				},
				TopOSMFeatures: {
					options: {
						variant: 'toposm-features',
						bounds: [[22, -132], [51, -56]],
						opacity: 0.9
					}
				}
			}
		},
		Esri: {
			url: '//server.arcgisonline.com/ArcGIS/rest/services/{variant}/MapServer/tile/{z}/{y}/{x}',
			options: {
				variant: 'World_Street_Map',
				attribution: 'Tiles &copy; Esri'
			},
			variants: {
				WorldStreetMap: {
					options: {
						attribution:
							'{attribution.Esri} &mdash; ' +
							'Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
					}
				},
				DeLorme: {
					options: {
						variant: 'Specialty/DeLorme_World_Base_Map',
						minZoom: 1,
						maxZoom: 11,
						attribution: '{attribution.Esri} &mdash; Copyright: &copy;2012 DeLorme'
					}
				},
				WorldTopoMap: {
					options: {
						variant: 'World_Topo_Map',
						attribution:
							'{attribution.Esri} &mdash; ' +
							'Esri, DeLorme, NAVTEQ, TomTom, Intermap, iPC, USGS, FAO, NPS, NRCAN, GeoBase, Kadaster NL, Ordnance Survey, Esri Japan, METI, Esri China (Hong Kong), and the GIS User Community'
					}
				},
				WorldImagery: {
					options: {
						variant: 'World_Imagery',
						attribution:
							'{attribution.Esri} &mdash; ' +
							'Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
					}
				},
				WorldTerrain: {
					options: {
						variant: 'World_Terrain_Base',
						maxZoom: 13,
						attribution:
							'{attribution.Esri} &mdash; ' +
							'Source: USGS, Esri, TANA, DeLorme, and NPS'
					}
				},
				WorldShadedRelief: {
					options: {
						variant: 'World_Shaded_Relief',
						maxZoom: 13,
						attribution: '{attribution.Esri} &mdash; Source: Esri'
					}
				},
				WorldPhysical: {
					options: {
						variant: 'World_Physical_Map',
						maxZoom: 8,
						attribution: '{attribution.Esri} &mdash; Source: US National Park Service'
					}
				},
				OceanBasemap: {
					options: {
						variant: 'Ocean_Basemap',
						maxZoom: 13,
						attribution: '{attribution.Esri} &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri'
					}
				},
				NatGeoWorldMap: {
					options: {
						variant: 'NatGeo_World_Map',
						maxZoom: 16,
						attribution: '{attribution.Esri} &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC'
					}
				},
				WorldGrayCanvas: {
					options: {
						variant: 'Canvas/World_Light_Gray_Base',
						maxZoom: 16,
						attribution: '{attribution.Esri} &mdash; Esri, DeLorme, NAVTEQ'
					}
				}
			}
		},
		OpenWeatherMap: {
			url: 'http://{s}.tile.openweathermap.org/map/{variant}/{z}/{x}/{y}.png',
			options: {
				maxZoom: 19,
				attribution: 'Map data &copy; <a href="http://openweathermap.org">OpenWeatherMap</a>',
				opacity: 0.5
			},
			variants: {
				Clouds: 'clouds',
				CloudsClassic: 'clouds_cls',
				Precipitation: 'precipitation',
				PrecipitationClassic: 'precipitation_cls',
				Rain: 'rain',
				RainClassic: 'rain_cls',
				Pressure: 'pressure',
				PressureContour: 'pressure_cntr',
				Wind: 'wind',
				Temperature: 'temp',
				Snow: 'snow'
			}
		},
		HERE: {
			/*
			 * HERE maps, formerly Nokia maps.
			 * These basemaps are free, but you need an API key. Please sign up at
			 * http://developer.here.com/getting-started
			 *
			 * Note that the base urls contain '.cit' whichs is HERE's
			 * 'Customer Integration Testing' environment. Please remove for production
			 * envirionments.
			 */
			url:
				'//{s}.{base}.maps.cit.api.here.com/maptile/2.1/' +
				'{type}/{mapID}/{variant}/{z}/{x}/{y}/{size}/{format}?' +
				'app_id={app_id}&app_code={app_code}&lg={language}',
			options: {
				attribution:
					'Map &copy; 1987-2014 <a href="http://developer.here.com">HERE</a>',
				subdomains: '1234',
				mapID: 'newest',
				'app_id': '<insert your app_id here>',
				'app_code': '<insert your app_code here>',
				base: 'base',
				variant: 'normal.day',
				maxZoom: 20,
				type: 'maptile',
				language: 'eng',
				format: 'png8',
				size: '256'
			},
			variants: {
				normalDay: 'normal.day',
				normalDayCustom: 'normal.day.custom',
				normalDayGrey: 'normal.day.grey',
				normalDayMobile: 'normal.day.mobile',
				normalDayGreyMobile: 'normal.day.grey.mobile',
				normalDayTransit: 'normal.day.transit',
				normalDayTransitMobile: 'normal.day.transit.mobile',
				normalNight: 'normal.night',
				normalNightMobile: 'normal.night.mobile',
				normalNightGrey: 'normal.night.grey',
				normalNightGreyMobile: 'normal.night.grey.mobile',

				basicMap: {
					options: {
						type: 'basetile'
					}
				},
				mapLabels: {
					options: {
						type: 'labeltile',
						format: 'png'
					}
				},
				trafficFlow: {
					options: {
						base: 'traffic',
						type: 'flowtile'
					}
				},
				carnavDayGrey: 'carnav.day.grey',
				hybridDay: {
					options: {
						base: 'aerial',
						variant: 'hybrid.day'
					}
				},
				hybridDayMobile: {
					options: {
						base: 'aerial',
						variant: 'hybrid.day.mobile'
					}
				},
				pedestrianDay: 'pedestrian.day',
				pedestrianNight: 'pedestrian.night',
				satelliteDay: {
					options: {
						base: 'aerial',
						variant: 'satellite.day'
					}
				},
				terrainDay: {
					options: {
						base: 'aerial',
						variant: 'terrain.day'
					}
				},
				terrainDayMobile: {
					options: {
						base: 'aerial',
						variant: 'terrain.day.mobile'
					}
				}
			}
		},
		Acetate: {
			url: 'http://a{s}.acetate.geoiq.com/tiles/{variant}/{z}/{x}/{y}.png',
			options: {
				attribution:
					'&copy;2012 Esri & Stamen, Data from OSM and Natural Earth',
				subdomains: '0123',
				minZoom: 2,
				maxZoom: 18,
				variant: 'acetate-base'
			},
			variants: {
				basemap: 'acetate-base',
				terrain: 'terrain',
				all: 'acetate-hillshading',
				foreground: 'acetate-fg',
				roads: 'acetate-roads',
				labels: 'acetate-labels',
				hillshading: 'hillshading'
			}
		},
		FreeMapSK: {
			url: 'http://t{s}.freemap.sk/T/{z}/{x}/{y}.jpeg',
			options: {
				minZoom: 8,
				maxZoom: 16,
				subdomains: '1234',
				bounds: [[47.204642, 15.996093], [49.830896, 22.576904]],
				attribution:
					'{attribution.OpenStreetMap}, vizualization CC-By-SA 2.0 <a href="http://freemap.sk">Freemap.sk</a>'
			}
		},
		MtbMap: {
			url: 'http://tile.mtbmap.cz/mtbmap_tiles/{z}/{x}/{y}.png',
			options: {
				attribution:
					'{attribution.OpenStreetMap} &amp; USGS'
			}
		},
		CartoDB: {
			url: 'http://{s}.basemaps.cartocdn.com/{variant}/{z}/{x}/{y}.png',
			options: {
				attribution: '{attribution.OpenStreetMap} &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
				subdomains: 'abcd',
				maxZoom: 19,
				variant: 'light_all'
			},
			variants: {
				Positron: 'light_all',
				PositronNoLabels: 'light_nolabels',
				PositronOnlyLabels: 'light_only_labels',
				DarkMatter: 'dark_all',
				DarkMatterNoLabels: 'dark_nolabels',
				DarkMatterOnlyLabels: 'dark_only_labels'
			}
		},
		HikeBike: {
			url: 'http://{s}.tiles.wmflabs.org/{variant}/{z}/{x}/{y}.png',
			options: {
				maxZoom: 19,
				attribution: '{attribution.OpenStreetMap}',
				variant: 'hikebike'
			},
			variants: {
				HikeBike: {},
				HillShading: {
					options: {
						maxZoom: 15,
						variant: 'hillshading'
					}
				}
			}
		},
		BasemapAT: {
			url: '//maps{s}.wien.gv.at/basemap/{variant}/normal/google3857/{z}/{y}/{x}.{format}',
			options: {
				maxZoom: 19,
				attribution: 'Datenquelle: <a href="www.basemap.at">basemap.at</a>',
				subdomains: ['', '1', '2', '3', '4'],
				format: 'png',
				bounds: [[46.358770, 8.782379], [49.037872, 17.189532]],
				variant: 'geolandbasemap'
			},
			variants: {
				basemap: 'geolandbasemap',
				grau: 'bmapgrau',
				overlay: 'bmapoverlay',
				highdpi: {
					options: {
						variant: 'bmaphidpi',
						format: 'jpeg'
					}
				},
				orthofoto: {
					options: {
						variant: 'bmaporthofoto30cm',
						format: 'jpeg'
					}
				}
			}
		},
		NASAGIBS: {
			url: '//map1.vis.earthdata.nasa.gov/wmts-webmerc/{variant}/default/{time}/{tilematrixset}{maxZoom}/{z}/{y}/{x}.{format}',
			options: {
				attribution:
					'Imagery provided by services from the Global Imagery Browse Services (GIBS), operated by the NASA/GSFC/Earth Science Data and Information System ' +
					'(<a href="https://earthdata.nasa.gov">ESDIS</a>) with funding provided by NASA/HQ.',
				bounds: [[-85.0511287776, -179.999999975], [85.0511287776, 179.999999975]],
				minZoom: 1,
				maxZoom: 9,
				format: 'jpg',
				time: '',
				tilematrixset: 'GoogleMapsCompatible_Level'
			},
			variants: {
				ModisTerraTrueColorCR: 'MODIS_Terra_CorrectedReflectance_TrueColor',
				ModisTerraBands367CR: 'MODIS_Terra_CorrectedReflectance_Bands367',
				ViirsEarthAtNight2012: {
					options: {
						variant: 'VIIRS_CityLights_2012',
						maxZoom: 8
					}
				},
				ModisTerraLSTDay: {
					options: {
						variant: 'MODIS_Terra_Land_Surface_Temp_Day',
						format: 'png',
						maxZoom: 7,
						opacity: 0.75
					}
				},
				ModisTerraSnowCover: {
					options: {
						variant: 'MODIS_Terra_Snow_Cover',
						format: 'png',
						maxZoom: 8,
						opacity: 0.75
					}
				},
				ModisTerraAOD: {
					options: {
						variant: 'MODIS_Terra_Aerosol',
						format: 'png',
						maxZoom: 6,
						opacity: 0.75
					}
				},
				ModisTerraChlorophyll: {
					options: {
						variant: 'MODIS_Terra_Chlorophyll_A',
						format: 'png',
						maxZoom: 7,
						opacity: 0.75
					}
				}
			}
		},
		NLS: {
			// NLS maps are copyright National library of Scotland.
			// http://maps.nls.uk/projects/api/index.html
			// Please contact NLS for anything other than non-commercial low volume usage
			//
			// Map sources: Ordnance Survey 1:1m to 1:63K, 1920s-1940s
			//   z0-9  - 1:1m
			//  z10-11 - quarter inch (1:253440)
			//  z12-18 - one inch (1:63360)
			url: '//nls-{s}.tileserver.com/nls/{z}/{x}/{y}.jpg',
			options: {
				attribution: '<a href="http://geo.nls.uk/maps/">National Library of Scotland Historic Maps</a>',
				bounds: [[49.6, -12], [61.7, 3]],
				minZoom: 1,
				maxZoom: 18,
				subdomains: '0123',
			}
		}
	};

	L.tileLayer.provider = function (provider, options) {
		return new L.TileLayer.Provider(provider, options);
	};

	return L;
}));


/*
 * L.Control.GeoSearch - search for an address and zoom to its location
 * https://github.com/smeijer/L.GeoSearch
 */

L.GeoSearch = {};
L.GeoSearch.Provider = {};

L.GeoSearch.Result = function (x, y, label, bounds, details) {
    this.X = x;
    this.Y = y;
    this.Label = label;
    this.bounds = bounds;

    if (details)
        this.details = details;
};

L.Control.GeoSearch = L.Control.extend({
    options: {
        position: 'topcenter',
        showMarker: true,
        retainZoomLevel: false,
        draggable: false
    },

    _config: {
        country: '',
        searchLabel: 'search for address ...',
        notFoundMessage: 'Sorry, that address could not be found.',
        messageHideDelay: 3000,
        zoomLevel: 18
    },

    initialize: function (options) {
        L.Util.extend(this.options, options);
        L.Util.extend(this._config, options);
    },

    onAdd: function (map) {
        var $controlContainer = map._controlContainer,
            nodes = $controlContainer.childNodes,
            topCenter = false;

        for (var i = 0, len = nodes.length; i < len; i++) {
            var klass = nodes[i].className;
            if (/leaflet-top/.test(klass) && /leaflet-center/.test(klass)) {
                topCenter = true;
                break;
            }
        }

        if (!topCenter) {
            var tc = document.createElement('div');
            tc.className += 'leaflet-top leaflet-center';
            $controlContainer.appendChild(tc);
            map._controlCorners.topcenter = tc;
        }

        this._map = map;
        this._container = L.DomUtil.create('div', 'leaflet-control-geosearch');

        var searchbox = document.createElement('input');
        searchbox.id = 'leaflet-control-geosearch-qry';
        searchbox.type = 'text';
        searchbox.placeholder = this._config.searchLabel;
        this._searchbox = searchbox;

        var msgbox = document.createElement('div');
        msgbox.id = 'leaflet-control-geosearch-msg';
        msgbox.className = 'leaflet-control-geosearch-msg';
        this._msgbox = msgbox;

        var resultslist = document.createElement('ul');
        resultslist.id = 'leaflet-control-geosearch-results';
        this._resultslist = resultslist;

        this._msgbox.appendChild(this._resultslist);
        this._container.appendChild(this._searchbox);
        this._container.appendChild(this._msgbox);

        L.DomEvent
          .addListener(this._container, 'click', L.DomEvent.stop)
          .addListener(this._searchbox, 'keypress', this._onKeyUp, this);

        L.DomEvent.disableClickPropagation(this._container);

        return this._container;
    },

    geosearch: function (qry) {
        var that = this;
        try {
            var provider = this._config.provider;

            if(typeof provider.GetLocations == 'function') {
                var results = provider.GetLocations(qry, function(results) {
                    that._processResults(results);
                });
            }
            else {
                var url = provider.GetServiceUrl(qry);
                this.sendRequest(provider, url);
            }
        }
        catch (error) {
            this._printError(error);
        }
    },

    sendRequest: function (provider, url) {
        var that = this;

        window.parseLocation = function (response) {
            var results = provider.ParseJSON(response);
            that._processResults(results);

            document.body.removeChild(document.getElementById('getJsonP'));
            delete window.parseLocation;
        };

        function getJsonP (url) {
            url = url + '&callback=parseLocation';
            var script = document.createElement('script');
            script.id = 'getJsonP';
            script.src = url;
            script.async = true;
            document.body.appendChild(script);
        }

        if (XMLHttpRequest) {
            var xhr = new XMLHttpRequest();

            if ('withCredentials' in xhr) {
                var xhr = new XMLHttpRequest();

                xhr.onreadystatechange = function () {
                    if (xhr.readyState == 4) {
                        if (xhr.status == 200) {
                            var response = JSON.parse(xhr.responseText),
                                results = provider.ParseJSON(response);

                            that._processResults(results);
                        } else if (xhr.status == 0 || xhr.status == 400) {
                            getJsonP(url);
                        } else {
                            that._printError(xhr.responseText);
                        }
                    }
                };

                xhr.open('GET', url, true);
                xhr.send();
            } else if (XDomainRequest) {
                var xdr = new XDomainRequest();

                xdr.onerror = function (err) {
                    that._printError(err);
                };

                xdr.onload = function () {
                    var response = JSON.parse(xdr.responseText),
                        results = provider.ParseJSON(response);

                    that._processResults(results);
                };

                xdr.open('GET', url);
                xdr.send();
            } else {
                getJsonP(url);
            }
        }
    },

    _processResults: function(results) {
        if (results.length > 0) {
            this._map.fireEvent('geosearch_foundlocations', {Locations: results});
            this._showLocation(results[0]);
        } else {
            this._printError(this._config.notFoundMessage);
        }
    },

    _showLocation: function (location) {
        if (this.options.showMarker == true) {
            if (typeof this._positionMarker === 'undefined') {
                this._positionMarker = L.marker(
                    [location.Y, location.X],
                    {draggable: this.options.draggable}
                ).addTo(this._map);
            }
            else {
                this._positionMarker.setLatLng([location.Y, location.X]);
            }
        }
        if (!this.options.retainZoomLevel && location.bounds && location.bounds.isValid()) {
            this._map.fitBounds(location.bounds);
        }
        else {
            this._map.setView([location.Y, location.X], this._getZoomLevel(), false);
        }

        this._map.fireEvent('geosearch_showlocation', {
          Location: location,
          Marker : this._positionMarker
        });
    },

    _printError: function(message) {
        var elem = this._resultslist;
        elem.innerHTML = '<li>' + message + '</li>';
        elem.style.display = 'block';

        this._map.fireEvent('geosearch_error', {message: message});

        setTimeout(function () {
            elem.style.display = 'none';
        }, 3000);
    },

    _onKeyUp: function (e) {
        var esc = 27,
            enter = 13;

        if (e.keyCode === esc) { // escape key detection is unreliable
            this._searchbox.value = '';
            this._map._container.focus();
        } else if (e.keyCode === enter) {
            e.preventDefault();
            e.stopPropagation();

            this.geosearch(this._searchbox.value);
        }
    },

    _getZoomLevel: function() {
        if (! this.options.retainZoomLevel) {
            return this._config.zoomLevel;
        }
        return this._map.zoom;
    }

});


/**
 * L.Control.GeoSearch - search for an address and zoom to it's location
 * L.GeoSearch.Provider.Esri uses arcgis geocoding service
 * https://github.com/smeijer/L.GeoSearch
 */

L.GeoSearch.Provider.Esri = L.Class.extend({
    options: {

    },

    initialize: function(options) {
        options = L.Util.setOptions(this, options);
    },
    
    GetServiceUrl: function (qry) {
        var parameters = L.Util.extend({
            text: qry,
            f: 'pjson'
        }, this.options);

        return location.protocol 
            + '//geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/find'
            + L.Util.getParamString(parameters);
    },

    ParseJSON: function (data) {
        if (data.locations.length == 0)
            return [];
        
        var results = [];
        for (var i = 0; i < data.locations.length; i++)
            results.push(new L.GeoSearch.Result(
                data.locations[i].feature.geometry.x, 
                data.locations[i].feature.geometry.y, 
                data.locations[i].name
            ));
        
        return results;
    }
});


/*
 Leaflet.markercluster, Provides Beautiful Animated Marker Clustering functionality for Leaflet, a JS library for interactive maps.
 https://github.com/Leaflet/Leaflet.markercluster
 (c) 2012-2013, Dave Leaver, smartrak
*/
(function (window, document, undefined) {
/*
 * L.MarkerClusterGroup extends L.FeatureGroup by clustering the markers contained within
 */

L.MarkerClusterGroup = L.FeatureGroup.extend({

	options: {
		maxClusterRadius: 80, //A cluster will cover at most this many pixels from its center
		iconCreateFunction: null,

		spiderfyOnMaxZoom: true,
		showCoverageOnHover: true,
		zoomToBoundsOnClick: true,
		singleMarkerMode: false,

		disableClusteringAtZoom: null,

		// Setting this to false prevents the removal of any clusters outside of the viewpoint, which
		// is the default behaviour for performance reasons.
		removeOutsideVisibleBounds: true,

		//Whether to animate adding markers after adding the MarkerClusterGroup to the map
		// If you are adding individual markers set to true, if adding bulk markers leave false for massive performance gains.
		animateAddingMarkers: false,

		//Increase to increase the distance away that spiderfied markers appear from the center
		spiderfyDistanceMultiplier: 1,

		//Options to pass to the L.Polygon constructor
		polygonOptions: {}
	},

	initialize: function (options) {
		L.Util.setOptions(this, options);
		if (!this.options.iconCreateFunction) {
			this.options.iconCreateFunction = this._defaultIconCreateFunction;
		}

		this._featureGroup = L.featureGroup();
		this._featureGroup.on(L.FeatureGroup.EVENTS, this._propagateEvent, this);

		this._nonPointGroup = L.featureGroup();
		this._nonPointGroup.on(L.FeatureGroup.EVENTS, this._propagateEvent, this);

		this._inZoomAnimation = 0;
		this._needsClustering = [];
		this._needsRemoving = []; //Markers removed while we aren't on the map need to be kept track of
		//The bounds of the currently shown area (from _getExpandedVisibleBounds) Updated on zoom/move
		this._currentShownBounds = null;

		this._queue = [];
	},

	addLayer: function (layer) {

		if (layer instanceof L.LayerGroup) {
			var array = [];
			for (var i in layer._layers) {
				array.push(layer._layers[i]);
			}
			return this.addLayers(array);
		}

		//Don't cluster non point data
		if (!layer.getLatLng) {
			this._nonPointGroup.addLayer(layer);
			return this;
		}

		if (!this._map) {
			this._needsClustering.push(layer);
			return this;
		}

		if (this.hasLayer(layer)) {
			return this;
		}


		//If we have already clustered we'll need to add this one to a cluster

		if (this._unspiderfy) {
			this._unspiderfy();
		}

		this._addLayer(layer, this._maxZoom);

		//Work out what is visible
		var visibleLayer = layer,
			currentZoom = this._map.getZoom();
		if (layer.__parent) {
			while (visibleLayer.__parent._zoom >= currentZoom) {
				visibleLayer = visibleLayer.__parent;
			}
		}

		if (this._currentShownBounds.contains(visibleLayer.getLatLng())) {
			if (this.options.animateAddingMarkers) {
				this._animationAddLayer(layer, visibleLayer);
			} else {
				this._animationAddLayerNonAnimated(layer, visibleLayer);
			}
		}
		return this;
	},

	removeLayer: function (layer) {

		if (layer instanceof L.LayerGroup)
		{
			var array = [];
			for (var i in layer._layers) {
				array.push(layer._layers[i]);
			}
			return this.removeLayers(array);
		}

		//Non point layers
		if (!layer.getLatLng) {
			this._nonPointGroup.removeLayer(layer);
			return this;
		}

		if (!this._map) {
			if (!this._arraySplice(this._needsClustering, layer) && this.hasLayer(layer)) {
				this._needsRemoving.push(layer);
			}
			return this;
		}

		if (!layer.__parent) {
			return this;
		}

		if (this._unspiderfy) {
			this._unspiderfy();
			this._unspiderfyLayer(layer);
		}

		//Remove the marker from clusters
		this._removeLayer(layer, true);

		if (this._featureGroup.hasLayer(layer)) {
			this._featureGroup.removeLayer(layer);
			if (layer.setOpacity) {
				layer.setOpacity(1);
			}
		}

		return this;
	},

	//Takes an array of markers and adds them in bulk
	addLayers: function (layersArray) {
		var i, l, m,
			onMap = this._map,
			fg = this._featureGroup,
			npg = this._nonPointGroup;

		for (i = 0, l = layersArray.length; i < l; i++) {
			m = layersArray[i];

			//Not point data, can't be clustered
			if (!m.getLatLng) {
				npg.addLayer(m);
				continue;
			}

			if (this.hasLayer(m)) {
				continue;
			}

			if (!onMap) {
				this._needsClustering.push(m);
				continue;
			}

			this._addLayer(m, this._maxZoom);

			//If we just made a cluster of size 2 then we need to remove the other marker from the map (if it is) or we never will
			if (m.__parent) {
				if (m.__parent.getChildCount() === 2) {
					var markers = m.__parent.getAllChildMarkers(),
						otherMarker = markers[0] === m ? markers[1] : markers[0];
					fg.removeLayer(otherMarker);
				}
			}
		}

		if (onMap) {
			//Update the icons of all those visible clusters that were affected
			fg.eachLayer(function (c) {
				if (c instanceof L.MarkerCluster && c._iconNeedsUpdate) {
					c._updateIcon();
				}
			});

			this._topClusterLevel._recursivelyAddChildrenToMap(null, this._zoom, this._currentShownBounds);
		}

		return this;
	},

	//Takes an array of markers and removes them in bulk
	removeLayers: function (layersArray) {
		var i, l, m,
			fg = this._featureGroup,
			npg = this._nonPointGroup;

		if (!this._map) {
			for (i = 0, l = layersArray.length; i < l; i++) {
				m = layersArray[i];
				this._arraySplice(this._needsClustering, m);
				npg.removeLayer(m);
			}
			return this;
		}

		for (i = 0, l = layersArray.length; i < l; i++) {
			m = layersArray[i];

			if (!m.__parent) {
				npg.removeLayer(m);
				continue;
			}

			this._removeLayer(m, true, true);

			if (fg.hasLayer(m)) {
				fg.removeLayer(m);
				if (m.setOpacity) {
					m.setOpacity(1);
				}
			}
		}

		//Fix up the clusters and markers on the map
		this._topClusterLevel._recursivelyAddChildrenToMap(null, this._zoom, this._currentShownBounds);

		fg.eachLayer(function (c) {
			if (c instanceof L.MarkerCluster) {
				c._updateIcon();
			}
		});

		return this;
	},

	//Removes all layers from the MarkerClusterGroup
	clearLayers: function () {
		//Need our own special implementation as the LayerGroup one doesn't work for us

		//If we aren't on the map (yet), blow away the markers we know of
		if (!this._map) {
			this._needsClustering = [];
			delete this._gridClusters;
			delete this._gridUnclustered;
		}

		if (this._noanimationUnspiderfy) {
			this._noanimationUnspiderfy();
		}

		//Remove all the visible layers
		this._featureGroup.clearLayers();
		this._nonPointGroup.clearLayers();

		this.eachLayer(function (marker) {
			delete marker.__parent;
		});

		if (this._map) {
			//Reset _topClusterLevel and the DistanceGrids
			this._generateInitialClusters();
		}

		return this;
	},

	//Override FeatureGroup.getBounds as it doesn't work
	getBounds: function () {
		var bounds = new L.LatLngBounds();
		if (this._topClusterLevel) {
			bounds.extend(this._topClusterLevel._bounds);
		} else {
			for (var i = this._needsClustering.length - 1; i >= 0; i--) {
				bounds.extend(this._needsClustering[i].getLatLng());
			}
		}

		bounds.extend(this._nonPointGroup.getBounds());

		return bounds;
	},

	//Overrides LayerGroup.eachLayer
	eachLayer: function (method, context) {
		var markers = this._needsClustering.slice(),
		    i;

		if (this._topClusterLevel) {
			this._topClusterLevel.getAllChildMarkers(markers);
		}

		for (i = markers.length - 1; i >= 0; i--) {
			method.call(context, markers[i]);
		}

		this._nonPointGroup.eachLayer(method, context);
	},

	//Overrides LayerGroup.getLayers
	getLayers: function () {
		var layers = [];
		this.eachLayer(function (l) {
			layers.push(l);
		});
		return layers;
	},

	//Overrides LayerGroup.getLayer, WARNING: Really bad performance
	getLayer: function (id) {
		var result = null;

		this.eachLayer(function (l) {
			if (L.stamp(l) === id) {
				result = l;
			}
		});

		return result;
	},

	//Returns true if the given layer is in this MarkerClusterGroup
	hasLayer: function (layer) {
		if (!layer) {
			return false;
		}

		var i, anArray = this._needsClustering;

		for (i = anArray.length - 1; i >= 0; i--) {
			if (anArray[i] === layer) {
				return true;
			}
		}

		anArray = this._needsRemoving;
		for (i = anArray.length - 1; i >= 0; i--) {
			if (anArray[i] === layer) {
				return false;
			}
		}

		return !!(layer.__parent && layer.__parent._group === this) || this._nonPointGroup.hasLayer(layer);
	},

	//Zoom down to show the given layer (spiderfying if necessary) then calls the callback
	zoomToShowLayer: function (layer, callback) {

		var showMarker = function () {
			if ((layer._icon || layer.__parent._icon) && !this._inZoomAnimation) {
				this._map.off('moveend', showMarker, this);
				this.off('animationend', showMarker, this);

				if (layer._icon) {
					callback();
				} else if (layer.__parent._icon) {
					var afterSpiderfy = function () {
						this.off('spiderfied', afterSpiderfy, this);
						callback();
					};

					this.on('spiderfied', afterSpiderfy, this);
					layer.__parent.spiderfy();
				}
			}
		};

		if (layer._icon && this._map.getBounds().contains(layer.getLatLng())) {
			callback();
		} else if (layer.__parent._zoom < this._map.getZoom()) {
			//Layer should be visible now but isn't on screen, just pan over to it
			this._map.on('moveend', showMarker, this);
			this._map.panTo(layer.getLatLng());
		} else {
			this._map.on('moveend', showMarker, this);
			this.on('animationend', showMarker, this);
			this._map.setView(layer.getLatLng(), layer.__parent._zoom + 1);
			layer.__parent.zoomToBounds();
		}
	},

	//Overrides FeatureGroup.onAdd
	onAdd: function (map) {
		this._map = map;
		var i, l, layer;

		if (!isFinite(this._map.getMaxZoom())) {
			throw "Map has no maxZoom specified";
		}

		this._featureGroup.onAdd(map);
		this._nonPointGroup.onAdd(map);

		if (!this._gridClusters) {
			this._generateInitialClusters();
		}

		for (i = 0, l = this._needsRemoving.length; i < l; i++) {
			layer = this._needsRemoving[i];
			this._removeLayer(layer, true);
		}
		this._needsRemoving = [];

		for (i = 0, l = this._needsClustering.length; i < l; i++) {
			layer = this._needsClustering[i];

			//If the layer doesn't have a getLatLng then we can't cluster it, so add it to our child featureGroup
			if (!layer.getLatLng) {
				this._featureGroup.addLayer(layer);
				continue;
			}


			if (layer.__parent) {
				continue;
			}
			this._addLayer(layer, this._maxZoom);
		}
		this._needsClustering = [];


		this._map.on('zoomend', this._zoomEnd, this);
		this._map.on('moveend', this._moveEnd, this);

		if (this._spiderfierOnAdd) { //TODO FIXME: Not sure how to have spiderfier add something on here nicely
			this._spiderfierOnAdd();
		}

		this._bindEvents();


		//Actually add our markers to the map:

		//Remember the current zoom level and bounds
		this._zoom = this._map.getZoom();
		this._currentShownBounds = this._getExpandedVisibleBounds();

		//Make things appear on the map
		this._topClusterLevel._recursivelyAddChildrenToMap(null, this._zoom, this._currentShownBounds);
	},

	//Overrides FeatureGroup.onRemove
	onRemove: function (map) {
		map.off('zoomend', this._zoomEnd, this);
		map.off('moveend', this._moveEnd, this);

		this._unbindEvents();

		//In case we are in a cluster animation
		this._map._mapPane.className = this._map._mapPane.className.replace(' leaflet-cluster-anim', '');

		if (this._spiderfierOnRemove) { //TODO FIXME: Not sure how to have spiderfier add something on here nicely
			this._spiderfierOnRemove();
		}



		//Clean up all the layers we added to the map
		this._hideCoverage();
		this._featureGroup.onRemove(map);
		this._nonPointGroup.onRemove(map);

		this._featureGroup.clearLayers();

		this._map = null;
	},

	getVisibleParent: function (marker) {
		var vMarker = marker;
		while (vMarker && !vMarker._icon) {
			vMarker = vMarker.__parent;
		}
		return vMarker || null;
	},

	//Remove the given object from the given array
	_arraySplice: function (anArray, obj) {
		for (var i = anArray.length - 1; i >= 0; i--) {
			if (anArray[i] === obj) {
				anArray.splice(i, 1);
				return true;
			}
		}
	},

	//Internal function for removing a marker from everything.
	//dontUpdateMap: set to true if you will handle updating the map manually (for bulk functions)
	_removeLayer: function (marker, removeFromDistanceGrid, dontUpdateMap) {
		var gridClusters = this._gridClusters,
			gridUnclustered = this._gridUnclustered,
			fg = this._featureGroup,
			map = this._map;

		//Remove the marker from distance clusters it might be in
		if (removeFromDistanceGrid) {
			for (var z = this._maxZoom; z >= 0; z--) {
				if (!gridUnclustered[z].removeObject(marker, map.project(marker.getLatLng(), z))) {
					break;
				}
			}
		}

		//Work our way up the clusters removing them as we go if required
		var cluster = marker.__parent,
			markers = cluster._markers,
			otherMarker;

		//Remove the marker from the immediate parents marker list
		this._arraySplice(markers, marker);

		while (cluster) {
			cluster._childCount--;

			if (cluster._zoom < 0) {
				//Top level, do nothing
				break;
			} else if (removeFromDistanceGrid && cluster._childCount <= 1) { //Cluster no longer required
				//We need to push the other marker up to the parent
				otherMarker = cluster._markers[0] === marker ? cluster._markers[1] : cluster._markers[0];

				//Update distance grid
				gridClusters[cluster._zoom].removeObject(cluster, map.project(cluster._cLatLng, cluster._zoom));
				gridUnclustered[cluster._zoom].addObject(otherMarker, map.project(otherMarker.getLatLng(), cluster._zoom));

				//Move otherMarker up to parent
				this._arraySplice(cluster.__parent._childClusters, cluster);
				cluster.__parent._markers.push(otherMarker);
				otherMarker.__parent = cluster.__parent;

				if (cluster._icon) {
					//Cluster is currently on the map, need to put the marker on the map instead
					fg.removeLayer(cluster);
					if (!dontUpdateMap) {
						fg.addLayer(otherMarker);
					}
				}
			} else {
				cluster._recalculateBounds();
				if (!dontUpdateMap || !cluster._icon) {
					cluster._updateIcon();
				}
			}

			cluster = cluster.__parent;
		}

		delete marker.__parent;
	},

	_isOrIsParent: function (el, oel) {
		while (oel) {
			if (el === oel) {
				return true;
			}
			oel = oel.parentNode;
		}
		return false;
	},

	_propagateEvent: function (e) {
		if (e.layer instanceof L.MarkerCluster) {
			//Prevent multiple clustermouseover/off events if the icon is made up of stacked divs (Doesn't work in ie <= 8, no relatedTarget)
			if (e.originalEvent && this._isOrIsParent(e.layer._icon, e.originalEvent.relatedTarget)) {
				return;
			}
			e.type = 'cluster' + e.type;
		}

		this.fire(e.type, e);
	},

	//Default functionality
	_defaultIconCreateFunction: function (cluster) {
		var childCount = cluster.getChildCount();

		var c = ' marker-cluster-';
		if (childCount < 10) {
			c += 'small';
		} else if (childCount < 100) {
			c += 'medium';
		} else {
			c += 'large';
		}

		return new L.DivIcon({ html: '<div><span>' + childCount + '</span></div>', className: 'marker-cluster' + c, iconSize: new L.Point(40, 40) });
	},

	_bindEvents: function () {
		var map = this._map,
		    spiderfyOnMaxZoom = this.options.spiderfyOnMaxZoom,
		    showCoverageOnHover = this.options.showCoverageOnHover,
		    zoomToBoundsOnClick = this.options.zoomToBoundsOnClick;

		//Zoom on cluster click or spiderfy if we are at the lowest level
		if (spiderfyOnMaxZoom || zoomToBoundsOnClick) {
			this.on('clusterclick', this._zoomOrSpiderfy, this);
		}

		//Show convex hull (boundary) polygon on mouse over
		if (showCoverageOnHover) {
			this.on('clustermouseover', this._showCoverage, this);
			this.on('clustermouseout', this._hideCoverage, this);
			map.on('zoomend', this._hideCoverage, this);
		}
	},

	_zoomOrSpiderfy: function (e) {
		var map = this._map;
		if (map.getMaxZoom() === map.getZoom()) {
			if (this.options.spiderfyOnMaxZoom) {
				e.layer.spiderfy();
			}
		} else if (this.options.zoomToBoundsOnClick) {
			e.layer.zoomToBounds();
		}

    // Focus the map again for keyboard users.
		if (e.originalEvent && e.originalEvent.keyCode === 13) {
			map._container.focus();
		}
	},

	_showCoverage: function (e) {
		var map = this._map;
		if (this._inZoomAnimation) {
			return;
		}
		if (this._shownPolygon) {
			map.removeLayer(this._shownPolygon);
		}
		if (e.layer.getChildCount() > 2 && e.layer !== this._spiderfied) {
			this._shownPolygon = new L.Polygon(e.layer.getConvexHull(), this.options.polygonOptions);
			map.addLayer(this._shownPolygon);
		}
	},

	_hideCoverage: function () {
		if (this._shownPolygon) {
			this._map.removeLayer(this._shownPolygon);
			this._shownPolygon = null;
		}
	},

	_unbindEvents: function () {
		var spiderfyOnMaxZoom = this.options.spiderfyOnMaxZoom,
			showCoverageOnHover = this.options.showCoverageOnHover,
			zoomToBoundsOnClick = this.options.zoomToBoundsOnClick,
			map = this._map;

		if (spiderfyOnMaxZoom || zoomToBoundsOnClick) {
			this.off('clusterclick', this._zoomOrSpiderfy, this);
		}
		if (showCoverageOnHover) {
			this.off('clustermouseover', this._showCoverage, this);
			this.off('clustermouseout', this._hideCoverage, this);
			map.off('zoomend', this._hideCoverage, this);
		}
	},

	_zoomEnd: function () {
		if (!this._map) { //May have been removed from the map by a zoomEnd handler
			return;
		}
		this._mergeSplitClusters();

		this._zoom = this._map._zoom;
		this._currentShownBounds = this._getExpandedVisibleBounds();
	},

	_moveEnd: function () {
		if (this._inZoomAnimation) {
			return;
		}

		var newBounds = this._getExpandedVisibleBounds();

		this._topClusterLevel._recursivelyRemoveChildrenFromMap(this._currentShownBounds, this._zoom, newBounds);
		this._topClusterLevel._recursivelyAddChildrenToMap(null, this._map._zoom, newBounds);

		this._currentShownBounds = newBounds;
		return;
	},

	_generateInitialClusters: function () {
		var maxZoom = this._map.getMaxZoom(),
			radius = this.options.maxClusterRadius;

		if (this.options.disableClusteringAtZoom) {
			maxZoom = this.options.disableClusteringAtZoom - 1;
		}
		this._maxZoom = maxZoom;
		this._gridClusters = {};
		this._gridUnclustered = {};

		//Set up DistanceGrids for each zoom
		for (var zoom = maxZoom; zoom >= 0; zoom--) {
			this._gridClusters[zoom] = new L.DistanceGrid(radius);
			this._gridUnclustered[zoom] = new L.DistanceGrid(radius);
		}

		this._topClusterLevel = new L.MarkerCluster(this, -1);
	},

	//Zoom: Zoom to start adding at (Pass this._maxZoom to start at the bottom)
	_addLayer: function (layer, zoom) {
		var gridClusters = this._gridClusters,
		    gridUnclustered = this._gridUnclustered,
		    markerPoint, z;

		if (this.options.singleMarkerMode) {
			layer.options.icon = this.options.iconCreateFunction({
				getChildCount: function () {
					return 1;
				},
				getAllChildMarkers: function () {
					return [layer];
				}
			});
		}

		//Find the lowest zoom level to slot this one in
		for (; zoom >= 0; zoom--) {
			markerPoint = this._map.project(layer.getLatLng(), zoom); // calculate pixel position

			//Try find a cluster close by
			var closest = gridClusters[zoom].getNearObject(markerPoint);
			if (closest) {
				closest._addChild(layer);
				layer.__parent = closest;
				return;
			}

			//Try find a marker close by to form a new cluster with
			closest = gridUnclustered[zoom].getNearObject(markerPoint);
			if (closest) {
				var parent = closest.__parent;
				if (parent) {
					this._removeLayer(closest, false);
				}

				//Create new cluster with these 2 in it

				var newCluster = new L.MarkerCluster(this, zoom, closest, layer);
				gridClusters[zoom].addObject(newCluster, this._map.project(newCluster._cLatLng, zoom));
				closest.__parent = newCluster;
				layer.__parent = newCluster;

				//First create any new intermediate parent clusters that don't exist
				var lastParent = newCluster;
				for (z = zoom - 1; z > parent._zoom; z--) {
					lastParent = new L.MarkerCluster(this, z, lastParent);
					gridClusters[z].addObject(lastParent, this._map.project(closest.getLatLng(), z));
				}
				parent._addChild(lastParent);

				//Remove closest from this zoom level and any above that it is in, replace with newCluster
				for (z = zoom; z >= 0; z--) {
					if (!gridUnclustered[z].removeObject(closest, this._map.project(closest.getLatLng(), z))) {
						break;
					}
				}

				return;
			}

			//Didn't manage to cluster in at this zoom, record us as a marker here and continue upwards
			gridUnclustered[zoom].addObject(layer, markerPoint);
		}

		//Didn't get in anything, add us to the top
		this._topClusterLevel._addChild(layer);
		layer.__parent = this._topClusterLevel;
		return;
	},

	//Enqueue code to fire after the marker expand/contract has happened
	_enqueue: function (fn) {
		this._queue.push(fn);
		if (!this._queueTimeout) {
			this._queueTimeout = setTimeout(L.bind(this._processQueue, this), 300);
		}
	},
	_processQueue: function () {
		for (var i = 0; i < this._queue.length; i++) {
			this._queue[i].call(this);
		}
		this._queue.length = 0;
		clearTimeout(this._queueTimeout);
		this._queueTimeout = null;
	},

	//Merge and split any existing clusters that are too big or small
	_mergeSplitClusters: function () {

		//Incase we are starting to split before the animation finished
		this._processQueue();

		if (this._zoom < this._map._zoom && this._currentShownBounds.contains(this._getExpandedVisibleBounds())) { //Zoom in, split
			this._animationStart();
			//Remove clusters now off screen
			this._topClusterLevel._recursivelyRemoveChildrenFromMap(this._currentShownBounds, this._zoom, this._getExpandedVisibleBounds());

			this._animationZoomIn(this._zoom, this._map._zoom);

		} else if (this._zoom > this._map._zoom) { //Zoom out, merge
			this._animationStart();

			this._animationZoomOut(this._zoom, this._map._zoom);
		} else {
			this._moveEnd();
		}
	},

	//Gets the maps visible bounds expanded in each direction by the size of the screen (so the user cannot see an area we do not cover in one pan)
	_getExpandedVisibleBounds: function () {
		if (!this.options.removeOutsideVisibleBounds) {
			return this.getBounds();
		}

		var map = this._map,
			bounds = map.getBounds(),
			sw = bounds._southWest,
			ne = bounds._northEast,
			latDiff = L.Browser.mobile ? 0 : Math.abs(sw.lat - ne.lat),
			lngDiff = L.Browser.mobile ? 0 : Math.abs(sw.lng - ne.lng);

		return new L.LatLngBounds(
			new L.LatLng(sw.lat - latDiff, sw.lng - lngDiff, true),
			new L.LatLng(ne.lat + latDiff, ne.lng + lngDiff, true));
	},

	//Shared animation code
	_animationAddLayerNonAnimated: function (layer, newCluster) {
		if (newCluster === layer) {
			this._featureGroup.addLayer(layer);
		} else if (newCluster._childCount === 2) {
			newCluster._addToMap();

			var markers = newCluster.getAllChildMarkers();
			this._featureGroup.removeLayer(markers[0]);
			this._featureGroup.removeLayer(markers[1]);
		} else {
			newCluster._updateIcon();
		}
	}
});

L.MarkerClusterGroup.include(!L.DomUtil.TRANSITION ? {

	//Non Animated versions of everything
	_animationStart: function () {
		//Do nothing...
	},
	_animationZoomIn: function (previousZoomLevel, newZoomLevel) {
		this._topClusterLevel._recursivelyRemoveChildrenFromMap(this._currentShownBounds, previousZoomLevel);
		this._topClusterLevel._recursivelyAddChildrenToMap(null, newZoomLevel, this._getExpandedVisibleBounds());
	},
	_animationZoomOut: function (previousZoomLevel, newZoomLevel) {
		this._topClusterLevel._recursivelyRemoveChildrenFromMap(this._currentShownBounds, previousZoomLevel);
		this._topClusterLevel._recursivelyAddChildrenToMap(null, newZoomLevel, this._getExpandedVisibleBounds());
	},
	_animationAddLayer: function (layer, newCluster) {
		this._animationAddLayerNonAnimated(layer, newCluster);
	}
} : {

	//Animated versions here
	_animationStart: function () {
		this._map._mapPane.className += ' leaflet-cluster-anim';
		this._inZoomAnimation++;
	},
	_animationEnd: function () {
		if (this._map) {
			this._map._mapPane.className = this._map._mapPane.className.replace(' leaflet-cluster-anim', '');
		}
		this._inZoomAnimation--;
		this.fire('animationend');
	},
	_animationZoomIn: function (previousZoomLevel, newZoomLevel) {
		var bounds = this._getExpandedVisibleBounds(),
		    fg = this._featureGroup,
		    i;

		//Add all children of current clusters to map and remove those clusters from map
		this._topClusterLevel._recursively(bounds, previousZoomLevel, 0, function (c) {
			var startPos = c._latlng,
				markers = c._markers,
				m;

			if (!bounds.contains(startPos)) {
				startPos = null;
			}

			if (c._isSingleParent() && previousZoomLevel + 1 === newZoomLevel) { //Immediately add the new child and remove us
				fg.removeLayer(c);
				c._recursivelyAddChildrenToMap(null, newZoomLevel, bounds);
			} else {
				//Fade out old cluster
				c.setOpacity(0);
				c._recursivelyAddChildrenToMap(startPos, newZoomLevel, bounds);
			}

			//Remove all markers that aren't visible any more
			//TODO: Do we actually need to do this on the higher levels too?
			for (i = markers.length - 1; i >= 0; i--) {
				m = markers[i];
				if (!bounds.contains(m._latlng)) {
					fg.removeLayer(m);
				}
			}

		});

		this._forceLayout();

		//Update opacities
		this._topClusterLevel._recursivelyBecomeVisible(bounds, newZoomLevel);
		//TODO Maybe? Update markers in _recursivelyBecomeVisible
		fg.eachLayer(function (n) {
			if (!(n instanceof L.MarkerCluster) && n._icon) {
				n.setOpacity(1);
			}
		});

		//update the positions of the just added clusters/markers
		this._topClusterLevel._recursively(bounds, previousZoomLevel, newZoomLevel, function (c) {
			c._recursivelyRestoreChildPositions(newZoomLevel);
		});

		//Remove the old clusters and close the zoom animation
		this._enqueue(function () {
			//update the positions of the just added clusters/markers
			this._topClusterLevel._recursively(bounds, previousZoomLevel, 0, function (c) {
				fg.removeLayer(c);
				c.setOpacity(1);
			});

			this._animationEnd();
		});
	},

	_animationZoomOut: function (previousZoomLevel, newZoomLevel) {
		this._animationZoomOutSingle(this._topClusterLevel, previousZoomLevel - 1, newZoomLevel);

		//Need to add markers for those that weren't on the map before but are now
		this._topClusterLevel._recursivelyAddChildrenToMap(null, newZoomLevel, this._getExpandedVisibleBounds());
		//Remove markers that were on the map before but won't be now
		this._topClusterLevel._recursivelyRemoveChildrenFromMap(this._currentShownBounds, previousZoomLevel, this._getExpandedVisibleBounds());
	},
	_animationZoomOutSingle: function (cluster, previousZoomLevel, newZoomLevel) {
		var bounds = this._getExpandedVisibleBounds();

		//Animate all of the markers in the clusters to move to their cluster center point
		cluster._recursivelyAnimateChildrenInAndAddSelfToMap(bounds, previousZoomLevel + 1, newZoomLevel);

		var me = this;

		//Update the opacity (If we immediately set it they won't animate)
		this._forceLayout();
		cluster._recursivelyBecomeVisible(bounds, newZoomLevel);

		//TODO: Maybe use the transition timing stuff to make this more reliable
		//When the animations are done, tidy up
		this._enqueue(function () {

			//This cluster stopped being a cluster before the timeout fired
			if (cluster._childCount === 1) {
				var m = cluster._markers[0];
				//If we were in a cluster animation at the time then the opacity and position of our child could be wrong now, so fix it
				m.setLatLng(m.getLatLng());
				m.setOpacity(1);
			} else {
				cluster._recursively(bounds, newZoomLevel, 0, function (c) {
					c._recursivelyRemoveChildrenFromMap(bounds, previousZoomLevel + 1);
				});
			}
			me._animationEnd();
		});
	},
	_animationAddLayer: function (layer, newCluster) {
		var me = this,
			fg = this._featureGroup;

		fg.addLayer(layer);
		if (newCluster !== layer) {
			if (newCluster._childCount > 2) { //Was already a cluster

				newCluster._updateIcon();
				this._forceLayout();
				this._animationStart();

				layer._setPos(this._map.latLngToLayerPoint(newCluster.getLatLng()));
				layer.setOpacity(0);

				this._enqueue(function () {
					fg.removeLayer(layer);
					layer.setOpacity(1);

					me._animationEnd();
				});

			} else { //Just became a cluster
				this._forceLayout();

				me._animationStart();
				me._animationZoomOutSingle(newCluster, this._map.getMaxZoom(), this._map.getZoom());
			}
		}
	},

	//Force a browser layout of stuff in the map
	// Should apply the current opacity and location to all elements so we can update them again for an animation
	_forceLayout: function () {
		//In my testing this works, infact offsetWidth of any element seems to work.
		//Could loop all this._layers and do this for each _icon if it stops working

		L.Util.falseFn(document.body.offsetWidth);
	}
});

L.markerClusterGroup = function (options) {
	return new L.MarkerClusterGroup(options);
};


L.MarkerCluster = L.Marker.extend({
	initialize: function (group, zoom, a, b) {

		L.Marker.prototype.initialize.call(this, a ? (a._cLatLng || a.getLatLng()) : new L.LatLng(0, 0), { icon: this });


		this._group = group;
		this._zoom = zoom;

		this._markers = [];
		this._childClusters = [];
		this._childCount = 0;
		this._iconNeedsUpdate = true;

		this._bounds = new L.LatLngBounds();

		if (a) {
			this._addChild(a);
		}
		if (b) {
			this._addChild(b);
		}
	},

	//Recursively retrieve all child markers of this cluster
	getAllChildMarkers: function (storageArray) {
		storageArray = storageArray || [];

		for (var i = this._childClusters.length - 1; i >= 0; i--) {
			this._childClusters[i].getAllChildMarkers(storageArray);
		}

		for (var j = this._markers.length - 1; j >= 0; j--) {
			storageArray.push(this._markers[j]);
		}

		return storageArray;
	},

	//Returns the count of how many child markers we have
	getChildCount: function () {
		return this._childCount;
	},

	//Zoom to the minimum of showing all of the child markers, or the extents of this cluster
	zoomToBounds: function () {
		var childClusters = this._childClusters.slice(),
			map = this._group._map,
			boundsZoom = map.getBoundsZoom(this._bounds),
			zoom = this._zoom + 1,
			mapZoom = map.getZoom(),
			i;

		//calculate how fare we need to zoom down to see all of the markers
		while (childClusters.length > 0 && boundsZoom > zoom) {
			zoom++;
			var newClusters = [];
			for (i = 0; i < childClusters.length; i++) {
				newClusters = newClusters.concat(childClusters[i]._childClusters);
			}
			childClusters = newClusters;
		}

		if (boundsZoom > zoom) {
			this._group._map.setView(this._latlng, zoom);
		} else if (boundsZoom <= mapZoom) { //If fitBounds wouldn't zoom us down, zoom us down instead
			this._group._map.setView(this._latlng, mapZoom + 1);
		} else {
			this._group._map.fitBounds(this._bounds);
		}
	},

	getBounds: function () {
		var bounds = new L.LatLngBounds();
		bounds.extend(this._bounds);
		return bounds;
	},

	_updateIcon: function () {
		this._iconNeedsUpdate = true;
		if (this._icon) {
			this.setIcon(this);
		}
	},

	//Cludge for Icon, we pretend to be an icon for performance
	createIcon: function () {
		if (this._iconNeedsUpdate) {
			this._iconObj = this._group.options.iconCreateFunction(this);
			this._iconNeedsUpdate = false;
		}
		return this._iconObj.createIcon();
	},
	createShadow: function () {
		return this._iconObj.createShadow();
	},


	_addChild: function (new1, isNotificationFromChild) {

		this._iconNeedsUpdate = true;
		this._expandBounds(new1);

		if (new1 instanceof L.MarkerCluster) {
			if (!isNotificationFromChild) {
				this._childClusters.push(new1);
				new1.__parent = this;
			}
			this._childCount += new1._childCount;
		} else {
			if (!isNotificationFromChild) {
				this._markers.push(new1);
			}
			this._childCount++;
		}

		if (this.__parent) {
			this.__parent._addChild(new1, true);
		}
	},

	//Expand our bounds and tell our parent to
	_expandBounds: function (marker) {
		var addedCount,
		    addedLatLng = marker._wLatLng || marker._latlng;

		if (marker instanceof L.MarkerCluster) {
			this._bounds.extend(marker._bounds);
			addedCount = marker._childCount;
		} else {
			this._bounds.extend(addedLatLng);
			addedCount = 1;
		}

		if (!this._cLatLng) {
			// when clustering, take position of the first point as the cluster center
			this._cLatLng = marker._cLatLng || addedLatLng;
		}

		// when showing clusters, take weighted average of all points as cluster center
		var totalCount = this._childCount + addedCount;

		//Calculate weighted latlng for display
		if (!this._wLatLng) {
			this._latlng = this._wLatLng = new L.LatLng(addedLatLng.lat, addedLatLng.lng);
		} else {
			this._wLatLng.lat = (addedLatLng.lat * addedCount + this._wLatLng.lat * this._childCount) / totalCount;
			this._wLatLng.lng = (addedLatLng.lng * addedCount + this._wLatLng.lng * this._childCount) / totalCount;
		}
	},

	//Set our markers position as given and add it to the map
	_addToMap: function (startPos) {
		if (startPos) {
			this._backupLatlng = this._latlng;
			this.setLatLng(startPos);
		}
		this._group._featureGroup.addLayer(this);
	},

	_recursivelyAnimateChildrenIn: function (bounds, center, maxZoom) {
		this._recursively(bounds, 0, maxZoom - 1,
			function (c) {
				var markers = c._markers,
					i, m;
				for (i = markers.length - 1; i >= 0; i--) {
					m = markers[i];

					//Only do it if the icon is still on the map
					if (m._icon) {
						m._setPos(center);
						m.setOpacity(0);
					}
				}
			},
			function (c) {
				var childClusters = c._childClusters,
					j, cm;
				for (j = childClusters.length - 1; j >= 0; j--) {
					cm = childClusters[j];
					if (cm._icon) {
						cm._setPos(center);
						cm.setOpacity(0);
					}
				}
			}
		);
	},

	_recursivelyAnimateChildrenInAndAddSelfToMap: function (bounds, previousZoomLevel, newZoomLevel) {
		this._recursively(bounds, newZoomLevel, 0,
			function (c) {
				c._recursivelyAnimateChildrenIn(bounds, c._group._map.latLngToLayerPoint(c.getLatLng()).round(), previousZoomLevel);

				//TODO: depthToAnimateIn affects _isSingleParent, if there is a multizoom we may/may not be.
				//As a hack we only do a animation free zoom on a single level zoom, if someone does multiple levels then we always animate
				if (c._isSingleParent() && previousZoomLevel - 1 === newZoomLevel) {
					c.setOpacity(1);
					c._recursivelyRemoveChildrenFromMap(bounds, previousZoomLevel); //Immediately remove our children as we are replacing them. TODO previousBounds not bounds
				} else {
					c.setOpacity(0);
				}

				c._addToMap();
			}
		);
	},

	_recursivelyBecomeVisible: function (bounds, zoomLevel) {
		this._recursively(bounds, 0, zoomLevel, null, function (c) {
			c.setOpacity(1);
		});
	},

	_recursivelyAddChildrenToMap: function (startPos, zoomLevel, bounds) {
		this._recursively(bounds, -1, zoomLevel,
			function (c) {
				if (zoomLevel === c._zoom) {
					return;
				}

				//Add our child markers at startPos (so they can be animated out)
				for (var i = c._markers.length - 1; i >= 0; i--) {
					var nm = c._markers[i];

					if (!bounds.contains(nm._latlng)) {
						continue;
					}

					if (startPos) {
						nm._backupLatlng = nm.getLatLng();

						nm.setLatLng(startPos);
						if (nm.setOpacity) {
							nm.setOpacity(0);
						}
					}

					c._group._featureGroup.addLayer(nm);
				}
			},
			function (c) {
				c._addToMap(startPos);
			}
		);
	},

	_recursivelyRestoreChildPositions: function (zoomLevel) {
		//Fix positions of child markers
		for (var i = this._markers.length - 1; i >= 0; i--) {
			var nm = this._markers[i];
			if (nm._backupLatlng) {
				nm.setLatLng(nm._backupLatlng);
				delete nm._backupLatlng;
			}
		}

		if (zoomLevel - 1 === this._zoom) {
			//Reposition child clusters
			for (var j = this._childClusters.length - 1; j >= 0; j--) {
				this._childClusters[j]._restorePosition();
			}
		} else {
			for (var k = this._childClusters.length - 1; k >= 0; k--) {
				this._childClusters[k]._recursivelyRestoreChildPositions(zoomLevel);
			}
		}
	},

	_restorePosition: function () {
		if (this._backupLatlng) {
			this.setLatLng(this._backupLatlng);
			delete this._backupLatlng;
		}
	},

	//exceptBounds: If set, don't remove any markers/clusters in it
	_recursivelyRemoveChildrenFromMap: function (previousBounds, zoomLevel, exceptBounds) {
		var m, i;
		this._recursively(previousBounds, -1, zoomLevel - 1,
			function (c) {
				//Remove markers at every level
				for (i = c._markers.length - 1; i >= 0; i--) {
					m = c._markers[i];
					if (!exceptBounds || !exceptBounds.contains(m._latlng)) {
						c._group._featureGroup.removeLayer(m);
						if (m.setOpacity) {
							m.setOpacity(1);
						}
					}
				}
			},
			function (c) {
				//Remove child clusters at just the bottom level
				for (i = c._childClusters.length - 1; i >= 0; i--) {
					m = c._childClusters[i];
					if (!exceptBounds || !exceptBounds.contains(m._latlng)) {
						c._group._featureGroup.removeLayer(m);
						if (m.setOpacity) {
							m.setOpacity(1);
						}
					}
				}
			}
		);
	},

	//Run the given functions recursively to this and child clusters
	// boundsToApplyTo: a L.LatLngBounds representing the bounds of what clusters to recurse in to
	// zoomLevelToStart: zoom level to start running functions (inclusive)
	// zoomLevelToStop: zoom level to stop running functions (inclusive)
	// runAtEveryLevel: function that takes an L.MarkerCluster as an argument that should be applied on every level
	// runAtBottomLevel: function that takes an L.MarkerCluster as an argument that should be applied at only the bottom level
	_recursively: function (boundsToApplyTo, zoomLevelToStart, zoomLevelToStop, runAtEveryLevel, runAtBottomLevel) {
		var childClusters = this._childClusters,
		    zoom = this._zoom,
			i, c;

		if (zoomLevelToStart > zoom) { //Still going down to required depth, just recurse to child clusters
			for (i = childClusters.length - 1; i >= 0; i--) {
				c = childClusters[i];
				if (boundsToApplyTo.intersects(c._bounds)) {
					c._recursively(boundsToApplyTo, zoomLevelToStart, zoomLevelToStop, runAtEveryLevel, runAtBottomLevel);
				}
			}
		} else { //In required depth

			if (runAtEveryLevel) {
				runAtEveryLevel(this);
			}
			if (runAtBottomLevel && this._zoom === zoomLevelToStop) {
				runAtBottomLevel(this);
			}

			//TODO: This loop is almost the same as above
			if (zoomLevelToStop > zoom) {
				for (i = childClusters.length - 1; i >= 0; i--) {
					c = childClusters[i];
					if (boundsToApplyTo.intersects(c._bounds)) {
						c._recursively(boundsToApplyTo, zoomLevelToStart, zoomLevelToStop, runAtEveryLevel, runAtBottomLevel);
					}
				}
			}
		}
	},

	_recalculateBounds: function () {
		var markers = this._markers,
			childClusters = this._childClusters,
			i;

		this._bounds = new L.LatLngBounds();
		delete this._wLatLng;

		for (i = markers.length - 1; i >= 0; i--) {
			this._expandBounds(markers[i]);
		}
		for (i = childClusters.length - 1; i >= 0; i--) {
			this._expandBounds(childClusters[i]);
		}
	},


	//Returns true if we are the parent of only one cluster and that cluster is the same as us
	_isSingleParent: function () {
		//Don't need to check this._markers as the rest won't work if there are any
		return this._childClusters.length > 0 && this._childClusters[0]._childCount === this._childCount;
	}
});



L.DistanceGrid = function (cellSize) {
	this._cellSize = cellSize;
	this._sqCellSize = cellSize * cellSize;
	this._grid = {};
	this._objectPoint = { };
};

L.DistanceGrid.prototype = {

	addObject: function (obj, point) {
		var x = this._getCoord(point.x),
		    y = this._getCoord(point.y),
		    grid = this._grid,
		    row = grid[y] = grid[y] || {},
		    cell = row[x] = row[x] || [],
		    stamp = L.Util.stamp(obj);

		this._objectPoint[stamp] = point;

		cell.push(obj);
	},

	updateObject: function (obj, point) {
		this.removeObject(obj);
		this.addObject(obj, point);
	},

	//Returns true if the object was found
	removeObject: function (obj, point) {
		var x = this._getCoord(point.x),
		    y = this._getCoord(point.y),
		    grid = this._grid,
		    row = grid[y] = grid[y] || {},
		    cell = row[x] = row[x] || [],
		    i, len;

		delete this._objectPoint[L.Util.stamp(obj)];

		for (i = 0, len = cell.length; i < len; i++) {
			if (cell[i] === obj) {

				cell.splice(i, 1);

				if (len === 1) {
					delete row[x];
				}

				return true;
			}
		}

	},

	eachObject: function (fn, context) {
		var i, j, k, len, row, cell, removed,
		    grid = this._grid;

		for (i in grid) {
			row = grid[i];

			for (j in row) {
				cell = row[j];

				for (k = 0, len = cell.length; k < len; k++) {
					removed = fn.call(context, cell[k]);
					if (removed) {
						k--;
						len--;
					}
				}
			}
		}
	},

	getNearObject: function (point) {
		var x = this._getCoord(point.x),
		    y = this._getCoord(point.y),
		    i, j, k, row, cell, len, obj, dist,
		    objectPoint = this._objectPoint,
		    closestDistSq = this._sqCellSize,
		    closest = null;

		for (i = y - 1; i <= y + 1; i++) {
			row = this._grid[i];
			if (row) {

				for (j = x - 1; j <= x + 1; j++) {
					cell = row[j];
					if (cell) {

						for (k = 0, len = cell.length; k < len; k++) {
							obj = cell[k];
							dist = this._sqDist(objectPoint[L.Util.stamp(obj)], point);
							if (dist < closestDistSq) {
								closestDistSq = dist;
								closest = obj;
							}
						}
					}
				}
			}
		}
		return closest;
	},

	_getCoord: function (x) {
		return Math.floor(x / this._cellSize);
	},

	_sqDist: function (p, p2) {
		var dx = p2.x - p.x,
		    dy = p2.y - p.y;
		return dx * dx + dy * dy;
	}
};


/* Copyright (c) 2012 the authors listed at the following URL, and/or
the authors of referenced articles or incorporated external code:
http://en.literateprograms.org/Quickhull_(Javascript)?action=history&offset=20120410175256

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Retrieved from: http://en.literateprograms.org/Quickhull_(Javascript)?oldid=18434
*/

(function () {
	L.QuickHull = {

		/*
		 * @param {Object} cpt a point to be measured from the baseline
		 * @param {Array} bl the baseline, as represented by a two-element
		 *   array of latlng objects.
		 * @returns {Number} an approximate distance measure
		 */
		getDistant: function (cpt, bl) {
			var vY = bl[1].lat - bl[0].lat,
				vX = bl[0].lng - bl[1].lng;
			return (vX * (cpt.lat - bl[0].lat) + vY * (cpt.lng - bl[0].lng));
		},

		/*
		 * @param {Array} baseLine a two-element array of latlng objects
		 *   representing the baseline to project from
		 * @param {Array} latLngs an array of latlng objects
		 * @returns {Object} the maximum point and all new points to stay
		 *   in consideration for the hull.
		 */
		findMostDistantPointFromBaseLine: function (baseLine, latLngs) {
			var maxD = 0,
				maxPt = null,
				newPoints = [],
				i, pt, d;

			for (i = latLngs.length - 1; i >= 0; i--) {
				pt = latLngs[i];
				d = this.getDistant(pt, baseLine);

				if (d > 0) {
					newPoints.push(pt);
				} else {
					continue;
				}

				if (d > maxD) {
					maxD = d;
					maxPt = pt;
				}
			}

			return { maxPoint: maxPt, newPoints: newPoints };
		},


		/*
		 * Given a baseline, compute the convex hull of latLngs as an array
		 * of latLngs.
		 *
		 * @param {Array} latLngs
		 * @returns {Array}
		 */
		buildConvexHull: function (baseLine, latLngs) {
			var convexHullBaseLines = [],
				t = this.findMostDistantPointFromBaseLine(baseLine, latLngs);

			if (t.maxPoint) { // if there is still a point "outside" the base line
				convexHullBaseLines =
					convexHullBaseLines.concat(
						this.buildConvexHull([baseLine[0], t.maxPoint], t.newPoints)
					);
				convexHullBaseLines =
					convexHullBaseLines.concat(
						this.buildConvexHull([t.maxPoint, baseLine[1]], t.newPoints)
					);
				return convexHullBaseLines;
			} else {  // if there is no more point "outside" the base line, the current base line is part of the convex hull
				return [baseLine[0]];
			}
		},

		/*
		 * Given an array of latlngs, compute a convex hull as an array
		 * of latlngs
		 *
		 * @param {Array} latLngs
		 * @returns {Array}
		 */
		getConvexHull: function (latLngs) {
			// find first baseline
			var maxLat = false, minLat = false,
				maxPt = null, minPt = null,
				i;

			for (i = latLngs.length - 1; i >= 0; i--) {
				var pt = latLngs[i];
				if (maxLat === false || pt.lat > maxLat) {
					maxPt = pt;
					maxLat = pt.lat;
				}
				if (minLat === false || pt.lat < minLat) {
					minPt = pt;
					minLat = pt.lat;
				}
			}
			var ch = [].concat(this.buildConvexHull([minPt, maxPt], latLngs),
								this.buildConvexHull([maxPt, minPt], latLngs));
			return ch;
		}
	};
}());

L.MarkerCluster.include({
	getConvexHull: function () {
		var childMarkers = this.getAllChildMarkers(),
			points = [],
			p, i;

		for (i = childMarkers.length - 1; i >= 0; i--) {
			p = childMarkers[i].getLatLng();
			points.push(p);
		}

		return L.QuickHull.getConvexHull(points);
	}
});


//This code is 100% based on https://github.com/jawj/OverlappingMarkerSpiderfier-Leaflet
//Huge thanks to jawj for implementing it first to make my job easy :-)

L.MarkerCluster.include({

	_2PI: Math.PI * 2,
	_circleFootSeparation: 25, //related to circumference of circle
	_circleStartAngle: Math.PI / 6,

	_spiralFootSeparation:  28, //related to size of spiral (experiment!)
	_spiralLengthStart: 11,
	_spiralLengthFactor: 5,

	_circleSpiralSwitchover: 9, //show spiral instead of circle from this marker count upwards.
								// 0 -> always spiral; Infinity -> always circle

	spiderfy: function () {
		if (this._group._spiderfied === this || this._group._inZoomAnimation) {
			return;
		}

		var childMarkers = this.getAllChildMarkers(),
			group = this._group,
			map = group._map,
			center = map.latLngToLayerPoint(this._latlng),
			positions;

		this._group._unspiderfy();
		this._group._spiderfied = this;

		//TODO Maybe: childMarkers order by distance to center

		if (childMarkers.length >= this._circleSpiralSwitchover) {
			positions = this._generatePointsSpiral(childMarkers.length, center);
		} else {
			center.y += 10; //Otherwise circles look wrong
			positions = this._generatePointsCircle(childMarkers.length, center);
		}

		this._animationSpiderfy(childMarkers, positions);
	},

	unspiderfy: function (zoomDetails) {
		/// <param Name="zoomDetails">Argument from zoomanim if being called in a zoom animation or null otherwise</param>
		if (this._group._inZoomAnimation) {
			return;
		}
		this._animationUnspiderfy(zoomDetails);

		this._group._spiderfied = null;
	},

	_generatePointsCircle: function (count, centerPt) {
		var circumference = this._group.options.spiderfyDistanceMultiplier * this._circleFootSeparation * (2 + count),
			legLength = circumference / this._2PI,  //radius from circumference
			angleStep = this._2PI / count,
			res = [],
			i, angle;

		res.length = count;

		for (i = count - 1; i >= 0; i--) {
			angle = this._circleStartAngle + i * angleStep;
			res[i] = new L.Point(centerPt.x + legLength * Math.cos(angle), centerPt.y + legLength * Math.sin(angle))._round();
		}

		return res;
	},

	_generatePointsSpiral: function (count, centerPt) {
		var legLength = this._group.options.spiderfyDistanceMultiplier * this._spiralLengthStart,
			separation = this._group.options.spiderfyDistanceMultiplier * this._spiralFootSeparation,
			lengthFactor = this._group.options.spiderfyDistanceMultiplier * this._spiralLengthFactor,
			angle = 0,
			res = [],
			i;

		res.length = count;

		for (i = count - 1; i >= 0; i--) {
			angle += separation / legLength + i * 0.0005;
			res[i] = new L.Point(centerPt.x + legLength * Math.cos(angle), centerPt.y + legLength * Math.sin(angle))._round();
			legLength += this._2PI * lengthFactor / angle;
		}
		return res;
	},

	_noanimationUnspiderfy: function () {
		var group = this._group,
			map = group._map,
			fg = group._featureGroup,
			childMarkers = this.getAllChildMarkers(),
			m, i;

		this.setOpacity(1);
		for (i = childMarkers.length - 1; i >= 0; i--) {
			m = childMarkers[i];

			fg.removeLayer(m);

			if (m._preSpiderfyLatlng) {
				m.setLatLng(m._preSpiderfyLatlng);
				delete m._preSpiderfyLatlng;
			}
			if (m.setZIndexOffset) {
				m.setZIndexOffset(0);
			}

			if (m._spiderLeg) {
				map.removeLayer(m._spiderLeg);
				delete m._spiderLeg;
			}
		}

		group._spiderfied = null;
	}
});

L.MarkerCluster.include(!L.DomUtil.TRANSITION ? {
	//Non Animated versions of everything
	_animationSpiderfy: function (childMarkers, positions) {
		var group = this._group,
			map = group._map,
			fg = group._featureGroup,
			i, m, leg, newPos;

		for (i = childMarkers.length - 1; i >= 0; i--) {
			newPos = map.layerPointToLatLng(positions[i]);
			m = childMarkers[i];

			m._preSpiderfyLatlng = m._latlng;
			m.setLatLng(newPos);
			if (m.setZIndexOffset) {
				m.setZIndexOffset(1000000); //Make these appear on top of EVERYTHING
			}

			fg.addLayer(m);


			leg = new L.Polyline([this._latlng, newPos], { weight: 1.5, color: '#222' });
			map.addLayer(leg);
			m._spiderLeg = leg;
		}
		this.setOpacity(0.3);
		group.fire('spiderfied');
	},

	_animationUnspiderfy: function () {
		this._noanimationUnspiderfy();
	}
} : {
	//Animated versions here
	SVG_ANIMATION: (function () {
		return document.createElementNS('http://www.w3.org/2000/svg', 'animate').toString().indexOf('SVGAnimate') > -1;
	}()),

	_animationSpiderfy: function (childMarkers, positions) {
		var me = this,
			group = this._group,
			map = group._map,
			fg = group._featureGroup,
			thisLayerPos = map.latLngToLayerPoint(this._latlng),
			i, m, leg, newPos;

		//Add markers to map hidden at our center point
		for (i = childMarkers.length - 1; i >= 0; i--) {
			m = childMarkers[i];

			//If it is a marker, add it now and we'll animate it out
			if (m.setOpacity) {
				m.setZIndexOffset(1000000); //Make these appear on top of EVERYTHING
				m.setOpacity(0);
			
				fg.addLayer(m);

				m._setPos(thisLayerPos);
			} else {
				//Vectors just get immediately added
				fg.addLayer(m);
			}
		}

		group._forceLayout();
		group._animationStart();

		var initialLegOpacity = L.Path.SVG ? 0 : 0.3,
			xmlns = L.Path.SVG_NS;


		for (i = childMarkers.length - 1; i >= 0; i--) {
			newPos = map.layerPointToLatLng(positions[i]);
			m = childMarkers[i];

			//Move marker to new position
			m._preSpiderfyLatlng = m._latlng;
			m.setLatLng(newPos);
			
			if (m.setOpacity) {
				m.setOpacity(1);
			}


			//Add Legs.
			leg = new L.Polyline([me._latlng, newPos], { weight: 1.5, color: '#222', opacity: initialLegOpacity });
			map.addLayer(leg);
			m._spiderLeg = leg;

			//Following animations don't work for canvas
			if (!L.Path.SVG || !this.SVG_ANIMATION) {
				continue;
			}

			//How this works:
			//http://stackoverflow.com/questions/5924238/how-do-you-animate-an-svg-path-in-ios
			//http://dev.opera.com/articles/view/advanced-svg-animation-techniques/

			//Animate length
			var length = leg._path.getTotalLength();
			leg._path.setAttribute("stroke-dasharray", length + "," + length);

			var anim = document.createElementNS(xmlns, "animate");
			anim.setAttribute("attributeName", "stroke-dashoffset");
			anim.setAttribute("begin", "indefinite");
			anim.setAttribute("from", length);
			anim.setAttribute("to", 0);
			anim.setAttribute("dur", 0.25);
			leg._path.appendChild(anim);
			anim.beginElement();

			//Animate opacity
			anim = document.createElementNS(xmlns, "animate");
			anim.setAttribute("attributeName", "stroke-opacity");
			anim.setAttribute("attributeName", "stroke-opacity");
			anim.setAttribute("begin", "indefinite");
			anim.setAttribute("from", 0);
			anim.setAttribute("to", 0.5);
			anim.setAttribute("dur", 0.25);
			leg._path.appendChild(anim);
			anim.beginElement();
		}
		me.setOpacity(0.3);

		//Set the opacity of the spiderLegs back to their correct value
		// The animations above override this until they complete.
		// If the initial opacity of the spiderlegs isn't 0 then they appear before the animation starts.
		if (L.Path.SVG) {
			this._group._forceLayout();

			for (i = childMarkers.length - 1; i >= 0; i--) {
				m = childMarkers[i]._spiderLeg;

				m.options.opacity = 0.5;
				m._path.setAttribute('stroke-opacity', 0.5);
			}
		}

		setTimeout(function () {
			group._animationEnd();
			group.fire('spiderfied');
		}, 200);
	},

	_animationUnspiderfy: function (zoomDetails) {
		var group = this._group,
			map = group._map,
			fg = group._featureGroup,
			thisLayerPos = zoomDetails ? map._latLngToNewLayerPoint(this._latlng, zoomDetails.zoom, zoomDetails.center) : map.latLngToLayerPoint(this._latlng),
			childMarkers = this.getAllChildMarkers(),
			svg = L.Path.SVG && this.SVG_ANIMATION,
			m, i, a;

		group._animationStart();

		//Make us visible and bring the child markers back in
		this.setOpacity(1);
		for (i = childMarkers.length - 1; i >= 0; i--) {
			m = childMarkers[i];

			//Marker was added to us after we were spidified
			if (!m._preSpiderfyLatlng) {
				continue;
			}

			//Fix up the location to the real one
			m.setLatLng(m._preSpiderfyLatlng);
			delete m._preSpiderfyLatlng;
			//Hack override the location to be our center
			if (m.setOpacity) {
				m._setPos(thisLayerPos);
				m.setOpacity(0);
			} else {
				fg.removeLayer(m);
			}

			//Animate the spider legs back in
			if (svg) {
				a = m._spiderLeg._path.childNodes[0];
				a.setAttribute('to', a.getAttribute('from'));
				a.setAttribute('from', 0);
				a.beginElement();

				a = m._spiderLeg._path.childNodes[1];
				a.setAttribute('from', 0.5);
				a.setAttribute('to', 0);
				a.setAttribute('stroke-opacity', 0);
				a.beginElement();

				m._spiderLeg._path.setAttribute('stroke-opacity', 0);
			}
		}

		setTimeout(function () {
			//If we have only <= one child left then that marker will be shown on the map so don't remove it!
			var stillThereChildCount = 0;
			for (i = childMarkers.length - 1; i >= 0; i--) {
				m = childMarkers[i];
				if (m._spiderLeg) {
					stillThereChildCount++;
				}
			}


			for (i = childMarkers.length - 1; i >= 0; i--) {
				m = childMarkers[i];

				if (!m._spiderLeg) { //Has already been unspiderfied
					continue;
				}


				if (m.setOpacity) {
					m.setOpacity(1);
					m.setZIndexOffset(0);
				}

				if (stillThereChildCount > 1) {
					fg.removeLayer(m);
				}

				map.removeLayer(m._spiderLeg);
				delete m._spiderLeg;
			}
			group._animationEnd();
		}, 200);
	}
});


L.MarkerClusterGroup.include({
	//The MarkerCluster currently spiderfied (if any)
	_spiderfied: null,

	_spiderfierOnAdd: function () {
		this._map.on('click', this._unspiderfyWrapper, this);

		if (this._map.options.zoomAnimation) {
			this._map.on('zoomstart', this._unspiderfyZoomStart, this);
		}
		//Browsers without zoomAnimation or a big zoom don't fire zoomstart
		this._map.on('zoomend', this._noanimationUnspiderfy, this);

		if (L.Path.SVG && !L.Browser.touch) {
			this._map._initPathRoot();
			//Needs to happen in the pageload, not after, or animations don't work in webkit
			//  http://stackoverflow.com/questions/8455200/svg-animate-with-dynamically-added-elements
			//Disable on touch browsers as the animation messes up on a touch zoom and isn't very noticable
		}
	},

	_spiderfierOnRemove: function () {
		this._map.off('click', this._unspiderfyWrapper, this);
		this._map.off('zoomstart', this._unspiderfyZoomStart, this);
		this._map.off('zoomanim', this._unspiderfyZoomAnim, this);

		this._unspiderfy(); //Ensure that markers are back where they should be
	},


	//On zoom start we add a zoomanim handler so that we are guaranteed to be last (after markers are animated)
	//This means we can define the animation they do rather than Markers doing an animation to their actual location
	_unspiderfyZoomStart: function () {
		if (!this._map) { //May have been removed from the map by a zoomEnd handler
			return;
		}

		this._map.on('zoomanim', this._unspiderfyZoomAnim, this);
	},
	_unspiderfyZoomAnim: function (zoomDetails) {
		//Wait until the first zoomanim after the user has finished touch-zooming before running the animation
		if (L.DomUtil.hasClass(this._map._mapPane, 'leaflet-touching')) {
			return;
		}

		this._map.off('zoomanim', this._unspiderfyZoomAnim, this);
		this._unspiderfy(zoomDetails);
	},


	_unspiderfyWrapper: function () {
		/// <summary>_unspiderfy but passes no arguments</summary>
		this._unspiderfy();
	},

	_unspiderfy: function (zoomDetails) {
		if (this._spiderfied) {
			this._spiderfied.unspiderfy(zoomDetails);
		}
	},

	_noanimationUnspiderfy: function () {
		if (this._spiderfied) {
			this._spiderfied._noanimationUnspiderfy();
		}
	},

	//If the given layer is currently being spiderfied then we unspiderfy it so it isn't on the map anymore etc
	_unspiderfyLayer: function (layer) {
		if (layer._spiderLeg) {
			this._featureGroup.removeLayer(layer);

			layer.setOpacity(1);
			//Position will be fixed up immediately in _animationUnspiderfy
			layer.setZIndexOffset(0);

			this._map.removeLayer(layer._spiderLeg);
			delete layer._spiderLeg;
		}
	}
});


}(window, document));

/*
  Leaflet.AwesomeMarkers, a plugin that adds colorful iconic markers for Leaflet, based on the Font Awesome icons
  (c) 2012-2013, Lennard Voogdt

  http://leafletjs.com
  https://github.com/lvoogdt
*/

/*global L*/

(function (window, document, undefined) {
    "use strict";
    /*
     * Leaflet.AwesomeMarkers assumes that you have already included the Leaflet library.
     */

    L.AwesomeMarkers = {};

    L.AwesomeMarkers.version = '2.0.1';

    L.AwesomeMarkers.Icon = L.Icon.extend({
        options: {
            iconSize: [35, 45],
            iconAnchor:   [17, 42],
            popupAnchor: [1, -32],
            shadowAnchor: [10, 12],
            shadowSize: [36, 16],
            className: 'awesome-marker',
            prefix: 'glyphicon',
            spinClass: 'fa-spin',
            extraClasses: '',
            icon: 'home',
            markerColor: 'blue',
            iconColor: 'white'
        },

        initialize: function (options) {
            options = L.Util.setOptions(this, options);
        },

        createIcon: function () {
            var div = document.createElement('div'),
                options = this.options;

            if (options.icon) {
                div.innerHTML = this._createInner();
            }

            if (options.bgPos) {
                div.style.backgroundPosition =
                    (-options.bgPos.x) + 'px ' + (-options.bgPos.y) + 'px';
            }

            this._setIconStyles(div, 'icon-' + options.markerColor);
            return div;
        },

        _createInner: function() {
            var iconClass, iconSpinClass = "", iconColorClass = "", iconColorStyle = "", options = this.options;

            if(options.icon.slice(0,options.prefix.length+1) === options.prefix + "-") {
                iconClass = options.icon;
            } else {
                iconClass = options.prefix + "-" + options.icon;
            }

            if(options.spin && typeof options.spinClass === "string") {
                iconSpinClass = options.spinClass;
            }

            if(options.iconColor) {
                if(options.iconColor === 'white' || options.iconColor === 'black') {
                    iconColorClass = "icon-" + options.iconColor;
                } else {
                    iconColorStyle = "style='color: " + options.iconColor + "' ";
                }
            }

            return "<i " + iconColorStyle + "class='" + options.extraClasses + " " + options.prefix + " " + iconClass + " " + iconSpinClass + " " + iconColorClass + "'></i>";
        },

        _setIconStyles: function (img, name) {
            var options = this.options,
                size = L.point(options[name === 'shadow' ? 'shadowSize' : 'iconSize']),
                anchor;

            if (name === 'shadow') {
                anchor = L.point(options.shadowAnchor || options.iconAnchor);
            } else {
                anchor = L.point(options.iconAnchor);
            }

            if (!anchor && size) {
                anchor = size.divideBy(2, true);
            }

            img.className = 'awesome-marker-' + name + ' ' + options.className;

            if (anchor) {
                img.style.marginLeft = (-anchor.x) + 'px';
                img.style.marginTop  = (-anchor.y) + 'px';
            }

            if (size) {
                img.style.width  = size.x + 'px';
                img.style.height = size.y + 'px';
            }
        },

        createShadow: function () {
            var div = document.createElement('div');

            this._setIconStyles(div, 'shadow');
            return div;
      }
    });
        
    L.AwesomeMarkers.icon = function (options) {
        return new L.AwesomeMarkers.Icon(options);
    };

}(this, document));





/* - ++resource++plone.formwidget.geolocation/maps.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/++resource++plone.formwidget.geolocation/maps.js?original=1
(function($){"use strict";var _initialize_map=function(el){var editable,map,baseLayers,markers,bounds,geosearch,map_wrap;map_wrap=$(el).closest('div.geolocation_wrapper');editable=map_wrap.hasClass('edit');var update_inputs=function(lat,lng){map_wrap.find('input.latitude').attr('value',lat);map_wrap.find('input.longitude').attr('value',lng)};var bind_draggable_marker=function(marker){marker.on('dragend', function(e){var coords=e.target.getLatLng();update_inputs(coords.lat,coords.lng)})};var create_markers=function(geopoints,editable){var markers=new L.MarkerClusterGroup();for(var i=0,size=geopoints.length;i<size ;i++){var geopoint=geopoints[i],marker;marker=new L.Marker([geopoint.lat,geopoint.lng],{icon:green_marker,draggable:editable});if(geopoint.popup){marker.bindPopup(geopoint.popup)}
if(editable){bind_draggable_marker(marker)}
markers.addLayer(marker)}
return markers};map=new L.Map(el,{fullscreenControl:true});L.Icon.Default.imagePath='++resource++plone.formwidget.geolocation/images';baseLayers={'Map':L.tileLayer.provider('OpenStreetMap.Mapnik'),'Satellite':L.tileLayer.provider('Esri.WorldImagery'),'Topographic':L.tileLayer.provider('OpenTopoMap'),'Toner':L.tileLayer.provider('Stamen.Toner'),};baseLayers['Map'].addTo(map);L.control.layers(baseLayers).addTo(map);var green_marker=L.AwesomeMarkers.icon({markerColor:'green'});var geopoints=$(el).data().geopoints;var markers=create_markers(geopoints,editable);map.addLayer(markers);bounds=markers.getBounds();map.fitBounds(bounds);if(editable){map.on('geosearch_showlocation', function(e){map.removeLayer(markers);var coords=e.Location;update_inputs(coords.Y,coords.X);bind_draggable_marker(e.Marker)});geosearch=new L.Control.GeoSearch({showMarker:true,draggable:editable,provider:new L.GeoSearch.Provider.Esri()});geosearch.addTo(map)}};var initialize_map=function(){$('.map').each(function(){_initialize_map(this)})};window.plone_formwidget_geolocation__initialize_map=initialize_map;$(document).ready(function(){initialize_map()})}(jQuery));

/* - ++resource++jquery.cookie.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/++resource++jquery.cookie.js?original=1
jQuery.cookie=function(b,j,m){if(typeof j!="undefined"){m=m||{};if(j===null){j="";m.expires=-1}var e="";if(m.expires&&(typeof m.expires=="number"||m.expires.toUTCString)){var f;if(typeof m.expires=="number"){f=new Date();f.setTime(f.getTime()+(m.expires*24*60*60*1000))}else{f=m.expires}e="; expires="+f.toUTCString()}var l=m.path?"; path="+(m.path):"";var g=m.domain?"; domain="+(m.domain):"";var a=m.secure?"; secure":"";document.cookie=[b,"=",encodeURIComponent(j),e,l,g,a].join("")}else{var d=null;if(document.cookie&&document.cookie!=""){var k=document.cookie.split(";");for(var h=0;h<k.length;h++){var c=jQuery.trim(k[h]);if(c.substring(0,b.length+1)==(b+"=")){d=decodeURIComponent(c.substring(b.length+1));break}}}return d}};

/* - ++resource++jquery.ajaxfileupload.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/++resource++jquery.ajaxfileupload.js?original=1
(function(){var d=document,w=window;
function get(element){if(typeof element=="string")
element=d.getElementById(element);return element}
function addEvent(el,type,fn){if(w.addEventListener){el.addEventListener(type,fn,false)} else if(w.attachEvent){var f=function(){fn.call(el,w.event)};el.attachEvent('on'+type,f)}}
var toElement=function(){var div=d.createElement('div');return function(html){div.innerHTML=html;var el=div.childNodes[0];div.removeChild(el);return el}}();
function hasClass(ele,cls){return ele.className.match(new RegExp('(\\s|^)'+cls+'(\\s|$)'))}
function addClass(ele,cls){if(!hasClass(ele,cls)) ele.className+=" "+cls}
function removeClass(ele,cls){var reg=new RegExp('(\\s|^)'+cls+'(\\s|$)');ele.className=ele.className.replace(reg,' ')}
if(document.documentElement["getBoundingClientRect"]){var getOffset=function(el){var box=el.getBoundingClientRect(),doc=el.ownerDocument,body=doc.body,docElem=doc.documentElement,clientTop=docElem.clientTop||body.clientTop||0,clientLeft=docElem.clientLeft||body.clientLeft||0,zoom=1;if(body.getBoundingClientRect){var bound=body.getBoundingClientRect();zoom=(bound.right-bound.left)/body.clientWidth}
if(zoom>1){clientTop=0;clientLeft=0}
var top=box.top/zoom+(window.pageYOffset||docElem&&docElem.scrollTop/zoom||body.scrollTop/zoom)-clientTop,left=box.left/zoom+(window.pageXOffset||docElem&&docElem.scrollLeft/zoom||body.scrollLeft/zoom)-clientLeft;return{top:top,left:left}}} else{var getOffset=function(el){if(w.jQuery){return jQuery(el).offset()}
var top=0,left=0;do{top+=el.offsetTop||0;left+=el.offsetLeft||0}
while(el=el.offsetParent);return{left:left,top:top}}}
function getBox(el){var left,right,top,bottom;var offset=getOffset(el);left=offset.left;top=offset.top;right=left+el.offsetWidth;bottom=top+el.offsetHeight;return{left:left,right:right,top:top,bottom:bottom}}
function getMouseCoords(e){if(!e.pageX&&e.clientX){var zoom=1;var body=document.body;if(body.getBoundingClientRect){var bound=body.getBoundingClientRect();zoom=(bound.right-bound.left)/body.clientWidth}
return{x:e.clientX/zoom+d.body.scrollLeft+d.documentElement.scrollLeft,y:e.clientY/zoom+d.body.scrollTop+d.documentElement.scrollTop}}
return{x:e.pageX,y:e.pageY}}
var getUID=function(){var id=0;return function(){return 'ValumsAjaxUpload'+id++}}();
function fileFromPath(file){return file.replace(/.*(\/|\\)/,"")}
function getExt(file){return (/[.]/.exec(file))?/[^.]+$/.exec(file.toLowerCase()):''}
Ajax_upload=AjaxUpload=function(button,options){if(button.jquery){button=button[0]} else if(typeof button=="string"&&/^#.*/.test(button)){button=button.slice(1)}
button=get(button);this._input=null;this._button=button;this._disabled=false;this._submitting=false;this._justClicked=false;this._parentDialog=d.body;if(window.jQuery&&jQuery.ui&&jQuery.ui.dialog){var parentDialog=jQuery(self._button).parents('.ui-dialog-content');if(parentDialog.length){this._parentDialog=parentDialog[0]}}
this._settings={action:'upload.php',name:'userfile',data:{},autoSubmit:true,responseType:false,onChange: function(file,extension){},onSubmit: function(file,extension){},onComplete: function(file,response){}};for(var i in options){this._settings[i]=options[i]}
this._createInput();this._rerouteClicks()}
AjaxUpload.prototype={setData: function(data){this._settings.data=data},disable: function(){this._disabled=true},enable: function(){this._disabled=false},destroy: function(){if(this._input){if(this._input.parentNode){this._input.parentNode.removeChild(this._input)}
this._input=null}},_createInput: function(){var self=this;var input=d.createElement("input");input.setAttribute('type','file');input.setAttribute('name',this._settings.name);var styles={'position':'absolute','margin':'-5px 0 0 -175px','padding':0,'width':'220px','height':'30px','fontSize':'14px','opacity':0,'cursor':'pointer','display':'none','zIndex':2147483583};for(var i in styles){input.style[i]=styles[i]}
if(!(input.style.opacity==="0")){input.style.filter="alpha(opacity=0)"}
this._parentDialog.appendChild(input);addEvent(input,'change', function(){var file=fileFromPath(this.value);if(self._settings.onChange.call(self,file,getExt(file))==false){return}
if(self._settings.autoSubmit){self.submit()}});addEvent(input,'click', function(){self.justClicked=true;setTimeout(function(){self.justClicked=false},3000)});this._input=input},_rerouteClicks: function(){var self=this;var box,dialogOffset={top:0,left:0},over=false;addEvent(self._button,'mouseover', function(e){if(!self._input||over) return;over=true;box=getBox(self._button);if(self._parentDialog!=d.body){dialogOffset=getOffset(self._parentDialog)}});addEvent(document,'mousemove', function(e){var input=self._input;if(!input||!over) return;if(self._disabled){removeClass(self._button,'hover');input.style.display='none';return}
var c=getMouseCoords(e);if((c.x>=box.left)&&(c.x<=box.right)&&(c.y>=box.top)&&(c.y<=box.bottom)){input.style.top=c.y-dialogOffset.top+'px';input.style.left=c.x-dialogOffset.left+'px';input.style.display='block';addClass(self._button,'hover')} else{over=false;if(!self.justClicked){input.style.display='none'}
removeClass(self._button,'hover')}})},_createIframe: function(){var id=getUID();var iframe=toElement('<iframe src="javascript:false;" name="'+id+'" />');iframe.id=id;iframe.style.display='none';d.body.appendChild(iframe);return iframe},submit: function(){var self=this,settings=this._settings;if(this._input.value===''){return}
var file=fileFromPath(this._input.value);if(!(settings.onSubmit.call(this,file,getExt(file))==false)){var iframe=this._createIframe();var form=this._createForm(iframe);form.appendChild(this._input);form.submit();d.body.removeChild(form);form=null;this._input=null;this._createInput();var toDeleteFlag=false;addEvent(iframe,'load', function(e){if(iframe.src=="about:blank"){if(toDeleteFlag){setTimeout( function(){d.body.removeChild(iframe)},0)}
return}
var doc=iframe.contentDocument?iframe.contentDocument:frames[iframe.id].document;if(doc.readyState&&doc.readyState!='complete'){return}
if(doc.body&&doc.body.innerHTML=="false"){return}
var response;if(doc.XMLDocument){response=doc.XMLDocument} else if(doc.body){response=doc.body.innerHTML;if(settings.responseType=='json'){response=window["eval"]("("+response+")")}} else{var response=doc}
settings.onComplete.call(self,file,response);toDeleteFlag=true;iframe.src="about:blank"})} else{d.body.removeChild(this._input);this._input=null;this._createInput()}},_createForm: function(iframe){var settings=this._settings;var form=toElement('<form method="post" enctype="multipart/form-data"></form>');form.style.display='none';form.action=settings.action;form.target=iframe.name;d.body.appendChild(form);for(var prop in settings.data){var el=d.createElement("input");el.type='hidden';el.name=prop;el.value=settings.data[prop];form.appendChild(el)}
return form}}})();

/* - ++resource++jquery.bbq.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/++resource++jquery.bbq.js?original=1
(function($,r){var h,n=Array.prototype.slice,t=decodeURIComponent,a=$.param,j,c,m,y,b=$.bbq=$.bbq||{},s,x,k,e=$.event.special,d="hashchange",B="querystring",F="fragment",z="elemUrlAttr",l="href",w="src",p=/^.*\?|#.*$/g,u,H,g,i,C,E={};function G(I){return typeof I==="string"}function D(J){var I=n.call(arguments,1);return function(){return J.apply(this,I.concat(n.call(arguments)))}}function o(I){return I.replace(H,"$2")}function q(I){return I.replace(/(?:^[^?#]*\?([^#]*).*$)?.*/,"$1")}function f(K,P,I,L,J){var R,O,N,Q,M;if(L!==h){N=I.match(K?H:/^([^#?]*)\??([^#]*)(#?.*)/);M=N[3]||"";if(J===2&&G(L)){O=L.replace(K?u:p,"")}else{Q=m(N[2]);L=G(L)?m[K?F:B](L):L;O=J===2?L:J===1?$.extend({},L,Q):$.extend({},Q,L);O=j(O);if(K){O=O.replace(g,t)}}R=N[1]+(K?C:O||!N[1]?"?":"")+O+M}else{R=P(I!==h?I:location.href)}return R}a[B]=D(f,0,q);a[F]=c=D(f,1,o);a.sorted=j=function(J,K){var I=[],L={};$.each(a(J,K).split("&"),function(P,M){var O=M.replace(/(?:%5B|=).*$/,""),N=L[O];if(!N){N=L[O]=[];I.push(O)}N.push(M)});return $.map(I.sort(),function(M){return L[M]}).join("&")};c.noEscape=function(J){J=J||"";var I=$.map(J.split(""),encodeURIComponent);g=new RegExp(I.join("|"),"g")};c.noEscape(",/");c.ajaxCrawlable=function(I){if(I!==h){if(I){u=/^.*(?:#!|#)/;H=/^([^#]*)(?:#!|#)?(.*)$/;C="#!"}else{u=/^.*#/;H=/^([^#]*)#?(.*)$/;C="#"}i=!!I}return i};c.ajaxCrawlable(0);$.deparam=m=function(L,I){var K={},J={"true":!0,"false":!1,"null":null};$.each(L.replace(/\+/g," ").split("&"),function(O,T){var N=T.split("="),S=t(N[0]),M,R=K,P=0,U=S.split("]["),Q=U.length-1;if(/\[/.test(U[0])&&/\]$/.test(U[Q])){U[Q]=U[Q].replace(/\]$/,"");U=U.shift().split("[").concat(U);Q=U.length-1}else{Q=0}if(N.length===2){M=t(N[1]);if(I){M=M&&!isNaN(M)?+M:M==="undefined"?h:J[M]!==h?J[M]:M}if(Q){for(;P<=Q;P++){S=U[P]===""?R.length:U[P];R=R[S]=P<Q?R[S]||(U[P+1]&&isNaN(U[P+1])?{}:[]):M}}else{if($.isArray(K[S])){K[S].push(M)}else{if(K[S]!==h){K[S]=[K[S],M]}else{K[S]=M}}}}else{if(S){K[S]=I?h:""}}});return K};function A(K,I,J){if(I===h||typeof I==="boolean"){J=I;I=a[K?F:B]()}else{I=G(I)?I.replace(K?u:p,""):I}return m(I,J)}m[B]=D(A,0);m[F]=y=D(A,1);$[z]||($[z]=function(I){return $.extend(E,I)})({a:l,base:l,iframe:w,img:w,input:w,form:"action",link:l,script:w});k=$[z];function v(L,J,K,I){if(!G(K)&&typeof K!=="object"){I=K;K=J;J=h}return this.each(function(){var O=$(this),M=J||k()[(this.nodeName||"").toLowerCase()]||"",N=M&&O.attr(M)||"";O.attr(M,a[L](N,K,I))})}$.fn[B]=D(v,B);$.fn[F]=D(v,F);b.pushState=s=function(L,I){if(G(L)&&/^#/.test(L)&&I===h){I=2}var K=L!==h,J=c(location.href,K?L:{},K?I:2);location.href=J};b.getState=x=function(I,J){return I===h||typeof I==="boolean"?y(I):y(J)[I]};b.removeState=function(I){var J={};if(I!==h){J=x();$.each($.isArray(I)?I:arguments,function(L,K){delete J[K]})}s(J,2)};e[d]=$.extend(e[d],{add:function(I){var K;function J(M){var L=M[F]=c();M.getState=function(N,O){return N===h||typeof N==="boolean"?m(L,N):m(L,O)[N]};K.apply(this,arguments)}if($.isFunction(I)){K=I;return J}else{K=I.handler;I.handler=J}}})})(jQuery,this);(function($,e,b){var c="hashchange",h=document,f,g=$.event.special,i=h.documentMode,d="on"+c in e&&(i===b||i>7);function a(j){j=j||location.href;return"#"+j.replace(/^[^#]*#?(.*)$/,"$1")}$.fn[c]=function(j){return j?this.bind(c,j):this.trigger(c)};$.fn[c].delay=50;g[c]=$.extend(g[c],{setup:function(){if(d){return false}$(f.start)},teardown:function(){if(d){return false}$(f.stop)}});f=(function(){var j={},p,m=a(),k=function(q){return q},l=k,o=k;j.start=function(){p||n()};j.stop=function(){p&&clearTimeout(p);p=b};function n(){var r=a(),q=o(m);if(r!==m){l(m=r,q);$(e).trigger(c)}else{if(q!==m){location.href=location.href.replace(/#.*/,"")+q}}p=setTimeout(n,$.fn[c].delay)}return j})()})(jQuery,this);

/* - ++resource++jquery.select2uislider.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/++resource++jquery.select2uislider.js?original=1
jQuery.fn.selectToUISlider=function(settings){var selects=jQuery(this);var options=jQuery.extend({labels:3,tooltip:true,tooltipSrc:'text',labelSrc:'value',sliderOptions:null},settings);var handleIds=(function(){var tempArr=[];selects.each(function(){tempArr.push('handle_'+jQuery(this).attr('id'))});return tempArr})();var selectOptions=(function(){var opts=[];selects.eq(0).find('option').each(function(){opts.push({value:jQuery(this).attr('value'),text:jQuery(this).text()})});return opts})();var groups=(function(){if(selects.eq(0).find('optgroup').size()>0){var groupedData=[];selects.eq(0).find('optgroup').each(function(i){groupedData[i]={};groupedData[i].label=jQuery(this).attr('label');groupedData[i].options=[];jQuery(this).find('option').each(function(){groupedData[i].options.push({text:jQuery(this).text(),value:jQuery(this).attr('value')})})});return groupedData}
else{return null}})();
function isArray(obj){return obj.constructor==Array}
function ttText(optIndex){return(options.tooltipSrc=='text')?selectOptions[optIndex].text:selectOptions[optIndex].value}
var sliderOptions={step:1,min:0,orientation:'horizontal',max:selectOptions.length-1,range:selects.length>1,slide: function(e,ui){var thisHandle=jQuery(ui.handle);var textval=ttText(ui.value);thisHandle.attr('aria-valuetext',textval).attr('aria-valuenow',ui.value).find('.ui-slider-tooltip .ttContent').text(textval);var currSelect=jQuery('#'+thisHandle.attr('id').split('handle_')[1]);currSelect.find('option').not(ui.value).prop('selected',false);currSelect.find('option').eq(ui.value).prop('selected',true)},values:(function(){var values=[];selects.each(function(){values.push(jQuery(this).get(0).selectedIndex)});return values})()};options.sliderOptions=(settings)?jQuery.extend(sliderOptions,settings.sliderOptions):sliderOptions;selects.bind('change keyup click', function(){var thisIndex=jQuery(this).get(0).selectedIndex;var thisHandle=jQuery('#handle_'+jQuery(this).attr('id'));var handleIndex=thisHandle.data('handleNum');thisHandle.parents('.ui-slider:eq(0)').slider("values",handleIndex,thisIndex)});var sliderComponent=jQuery('<div></div>');selects.each(function(i){var hidett='';var thisLabel=jQuery('label[for='+jQuery(this).attr('id')+']');var labelText=(thisLabel.size()>0)?'Slider control for '+thisLabel.text()+'':'';var thisLabelId=thisLabel.attr('id')||thisLabel.attr('id','label_'+handleIds[i]).attr('id');if(options.tooltip===false){hidett=' style="display: none;"'}
jQuery('<a '+'href="#" tabindex="0" '+'id="'+handleIds[i]+'" '+'class="ui-slider-handle" '+'role="slider" '+'aria-labelledby="'+thisLabelId+'" '+'aria-valuemin="'+options.sliderOptions.min+'" '+'aria-valuemax="'+options.sliderOptions.max+'" '+'aria-valuenow="'+options.sliderOptions.values[i]+'" '+'aria-valuetext="'+ttText(options.sliderOptions.values[i])+'" '+'><span class="screenReaderContext">'+labelText+'</span>'+'<span class="ui-slider-tooltip ui-widget-content ui-corner-all"'+hidett+'><span class="ttContent"></span>'+'<span class="ui-tooltip-pointer-down ui-widget-content"><span class="ui-tooltip-pointer-down-inner"></span></span>'+'</span></a>').data('handleNum',i).appendTo(sliderComponent)});if(groups){var inc=0;var scale=sliderComponent.append('<dl class="ui-slider-scale ui-helper-reset" role="presentation"></dl>').find('.ui-slider-scale:eq(0)');jQuery(groups).each(function(h){scale.append('<dt style="width: '+(100/groups.length).toFixed(2)+'%'+'; left:'+(h/(groups.length-1) * 100).toFixed(2)+'%'+'"><span>'+this.label+'</span></dt>');var groupOpts=this.options;jQuery(this.options).each(function(i){var style=(inc==selectOptions.length-1||inc===0)?'style="display: none;"':'' ;var labelText=(options.labelSrc=='text')?groupOpts[i].text:groupOpts[i].value;scale.append('<dd style="left:'+leftVal(inc)+'"><span class="ui-slider-label">'+labelText+'</span><span class="ui-slider-tic ui-widget-content"'+style+'></span></dd>');inc++})})}
else{var scale=sliderComponent.append('<ol class="ui-slider-scale ui-helper-reset" role="presentation"></ol>').find('.ui-slider-scale:eq(0)');jQuery(selectOptions).each(function(i){var style=(i==selectOptions.length-1||i===0)?'style="display: none;"':'' ;var labelText=(options.labelSrc=='text')?this.text:this.value;scale.append('<li style="left:'+leftVal(i)+'"><span class="ui-slider-label">'+labelText+'</span><span class="ui-slider-tic ui-widget-content"'+style+'></span></li>')})}
function leftVal(i){return(i/(selectOptions.length-1) * 100).toFixed(2)+'%'}
if(options.labels>1){sliderComponent.find('.ui-slider-scale li:last span.ui-slider-label, .ui-slider-scale dd:last span.ui-slider-label').addClass('ui-slider-label-show')}
var increm=Math.max(1,Math.round(selectOptions.length/options.labels));for(var j=0;j<selectOptions.length;j+=increm){if((selectOptions.length-j)>increm){sliderComponent.find('.ui-slider-scale li:eq('+j+') span.ui-slider-label, .ui-slider-scale dd:eq('+j+') span.ui-slider-label').addClass('ui-slider-label-show')}}
sliderComponent.find('.ui-slider-scale dt').each(function(i){jQuery(this).css({'left':((100/(groups.length))*i).toFixed(2)+'%'})});sliderComponent.insertAfter(jQuery(this).eq(this.length-1)).slider(options.sliderOptions).attr('role','application').find('.ui-slider-label').each(function(){jQuery(this).css('marginLeft',-jQuery(this).width()/2)});sliderComponent.find('.ui-tooltip-pointer-down-inner').each(function(){var bWidth=jQuery('.ui-tooltip-pointer-down-inner').css('borderTopWidth');var bColor=jQuery(this).parents('.ui-slider-tooltip').css('backgroundColor');jQuery(this).css('border-top',bWidth+' solid '+bColor)});var values=sliderComponent.slider('values');if(isArray(values)){jQuery(values).each(function(i){sliderComponent.find('.ui-slider-tooltip .ttContent').eq(i).text(ttText(this))})}
else{sliderComponent.find('.ui-slider-tooltip .ttContent').eq(0).text(ttText(values))}
return this};

/* - ++resource++jquery.tagcloud.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/++resource++jquery.tagcloud.js?original=1
;(function($){var oSettings;var oUlCss={};var oLiCss={};var fGAng=2.399963;$.tagcloud={id:"TagCloud",version:"0.5.0",defaults:{height:null,type:"cloud",sizemax:20,sizemin:10,colormax:"00F",colormin:"B4D2FF",seed:null,power:.5}};$.fn.extend({tagcloud: function(_settings){oSettings=$.extend({},$.tagcloud.defaults,_settings);if(oSettings.seed===null) oSettings.seed=Math.ceil(Math.random()*45309714203);switch(oSettings.type){case "sphere":case "cloud":oUlCss={position:"relative"};oLiCss={position:"absolute",display:"block"};break;case "list":oUlCss={height:"auto"};oLiCss={position:"static",display:"inline"};break}
Rng.setSeed(oSettings.seed+123456);return this.each(function(i,o){var mUl=$(o);var aLi=mUl.find(">li");var iNumLi=aLi.length;var iUlW=mUl.width();var iUlH=oSettings.height===null?(.004*iUlW*iNumLi):oSettings.height;mUl.css({width:iUlW,height:iUlH,listStyle:"none",margin:0,padding:0});mUl.css(oUlCss);var iValMx=-2147483647;var iValMn=2147483648;var iLastVal=-1;for(var j=0;j<iNumLi;j++){var mLi=$(aLi[j]);var iVal=mLi.attr("value")==-1?iLastVal++:mLi.attr("value");if(iVal>iValMx) iValMx=iVal;if(iVal<iValMn) iValMn=iVal;iLastVal=iVal}
var iValRn=iValMx-iValMn;var aLine=new Array();for(var j=0;j<iNumLi;j++) aLine[j]=j;for(var j,x,k=aLine.length;k;j=parseInt(Rng.rand(0,1000)/1000 * k),x=aLine[--k],aLine[k]=aLine[j],aLine[j]=x);iLastVal=-1;for(var j=0;j<iNumLi;j++){var mLi=$(aLi[j]);var iVal=mLi.attr("value")==-1?iLastVal++:mLi.attr("value");iLastVal=iVal;var fPrt=((iNumLi-j-1)/(iNumLi-1));var fPrt=(iVal-iValMn)/iValRn;var iSzFnt=oSettings.sizemin+fPrt*(oSettings.sizemax-oSettings.sizemin);var sColor=colorRng(oSettings.colormin,oSettings.colormax,fPrt);mLi.css({"fontSize":iSzFnt,position:"absolute",color:"#"+sColor,margin:0,padding:0}).children().css({color:"#"+sColor});var iLiW=mLi.width();var iLiH=mLi.height()
var oCss={};if(oSettings.type!="list"){if(oSettings.type=="cloud"){var iXps=Rng.rand(0,iUlW-iLiW);var iYps=aLine[j]*(iUlH/iNumLi)-iLiH/2} else{var fRds=Math.pow(j/iNumLi,oSettings.power);var fRad=(j+Math.PI/2)*fGAng;var iXps=iUlW/2-iLiW/2+.5*iUlW*fRds*Math.sin(fRad);var iYps=iUlH/2-iLiH/2+.5*iUlH*fRds*Math.cos(fRad)}
oCss.left=iXps;oCss.top=iYps}
for(var prop in oLiCss) oCss[prop]=oLiCss[prop];mLi.css(oCss)}})}});var Rng=new function(){this.seed=23145678901;this.A=48271;this.M=2147483647;this.Q=this.M/this.A;this.R=this.M%this.A;this.oneOverM=1.0/this.M}
Rng.setSeed=function(seed){this.seed=seed}
Rng.next=function(){var hi=this.seed/this.Q;var lo=this.seed%this.Q;var test=this.A*lo-this.R*hi;this.seed=test+(test>0?0:this.M);return(this.seed*this.oneOverM)}
Rng.rand=function(lrn,urn){return Math.floor((urn-lrn+1) * this.next()+lrn)}
function d2h(d){return d.toString(16)}
function h2d(h){return parseInt(h,16)}
function getRGB(s){var b3=s.length==3;var aClr=[];for(var i=0;i<3;i++){var sClr=s.substring(i*(b3?1:2),(i+1)*(b3?1:2));aClr.push(h2d(b3?sClr+sClr:sClr))}
return aClr}
function getHex(a){var s="";for(var i=0;i<3;i++){var c=d2h(a[i]);if(c.length==1) c="0"+c;s+=c}
return s}
function colorRng(mn,mx,prt){var aMin=getRGB(mn);var aMax=getRGB(mx);var aRtr=[];for(var i=0;i<3;i++) aRtr.push(aMin[i]+Math.floor(prt*(aMax[i]-aMin[i])));return getHex(aRtr)}
function trace(o){if(window.console&&window.console.log){if(typeof(o)=="string") window.console.log(o);else for(var prop in o) window.console.log(prop+": "+o[prop])}};$.fn.TagCloud=$.fn.Tagcloud=$.fn.tagcloud})(jQuery);

/* - faceted_view.js - */
// http://climate-adapt.eea.europa.eu/portal_javascripts/faceted_view.js?original=1
var Faceted={version:'2.0'};Faceted.Events={};Faceted.Events.INITIALIZE='FACETED-INITIALIZE';Faceted.Events.AJAX_QUERY_START='FACETED-AJAX-QUERY-START';Faceted.Events.AJAX_QUERY_SUCCESS='FACETED-AJAX-QUERY-SUCCESS';Faceted.Events.QUERY_INITIALIZED='FACETED-QUERY-INITIALIZED';Faceted.Events.QUERY_CHANGED='FACETED-QUERY-CHANGED';Faceted.Events.RESET='FACETED-RESET';Faceted.Events.FORM_DO_QUERY='FACETED-FORM-DO-QUERY';Faceted.Events.WINDOW_WIDTH_CHANGED='FACETED-WINDOW-WIDTH-CHANGED';Faceted.Events.WINDOW_HEIGHT_CHANGED='FACETED-WINDOW-HEIGHT-CHANGED';Faceted.Events.AJAX_START='FACETED-AJAX-START';Faceted.Events.AJAX_STOP='FACETED-AJAX-STOP';Faceted.Events.AJAX_ERROR='FACETED-AJAX-ERROR';Faceted.Events.REDRAW='FACETED-REDRAW';Faceted.Events.HASHCHANGE='hashchange.FACETED-HASHCHANGE';Faceted.Events.DO_UPDATE='FACETED-DO_UPDATE';Faceted.Events.cleanup=function(){jQuery(Faceted.Events).unbind(Faceted.Events.AJAX_QUERY_START);jQuery(Faceted.Events).unbind(Faceted.Events.AJAX_QUERY_SUCCESS);jQuery(Faceted.Events).unbind(Faceted.Events.QUERY_INITIALIZED);jQuery(Faceted.Events).unbind(Faceted.Events.QUERY_CHANGED);jQuery(Faceted.Events).unbind(Faceted.Events.RESET);jQuery(Faceted.Events).unbind(Faceted.Events.FORM_DO_QUERY);jQuery(Faceted.Events).unbind(Faceted.Events.WINDOW_WIDTH_CHANGED);jQuery(Faceted.Events).unbind(Faceted.Events.WINDOW_HEIGHT_CHANGED);jQuery(Faceted.Events).unbind(Faceted.Events.AJAX_START);jQuery(Faceted.Events).unbind(Faceted.Events.AJAX_STOP);jQuery(Faceted.Events).unbind(Faceted.Events.AJAX_ERROR);jQuery(Faceted.Events).unbind(Faceted.Events.REDRAW);jQuery(Faceted.Events).unbind(Faceted.Events.DO_UPDATE);jQuery(window).unbind(Faceted.Events.HASHCHANGE)};Faceted.Widgets={};Faceted.Query={};Faceted.BASEURL='';Faceted.Options={};Faceted.Options.SHOW_SPINNER=true;Faceted.Options.FADE_SPEED='slow';Faceted.SortedQuery=function(query){if(!query){query=Faceted.Query}
var keys=[];jQuery.each(query, function(key){if(!this||this=='all'){return}
keys.push(key)});keys.sort();var res={};jQuery.each(keys, function(index){res[this]=query[this]});return res};Faceted.Window={initialize: function(){this.width=jQuery(window).width();this.height=jQuery(window).height();var js_window=this;jQuery(window).resize(function(){js_window.width_change();js_window.height_change()});var fullscreen=jQuery('a:has(img#icon-full_screen)');if(fullscreen.length){js_window.toggle_fullscreen(fullscreen)}},width_change: function(){var width=jQuery(window).width();if(width!=this.width){this.width=width;jQuery(Faceted.Events).trigger(Faceted.Events.WINDOW_WIDTH_CHANGED,{width:width})}},height_change: function(){var height=jQuery(window).height();if(height!=this.height){this.height=height;jQuery(Faceted.Events).trigger(Faceted.Events.WINDOW_HEIGHT_CHANGED,{height:height})}},toggle_fullscreen: function(button){button.attr('href','#');button.click(function(evt){var toggleFullScreenMode=window.toggleFullScreenMode;if(toggleFullScreenMode){toggleFullScreenMode();jQuery(Faceted.Events).trigger(Faceted.Events.WINDOW_WIDTH_CHANGED)}
return false})}};Faceted.Form={initialize: function(){this.form=jQuery('#faceted-form');this.area=jQuery('#faceted-results');this.mode=this.form.attr('data-mode')||'view';this.version='';var version=jQuery('#faceted-version',this.form);if(version){this.version=version.text()}
this.area.ajaxError(function(event,request,settings){jQuery(this).html(''+'<h3>This site encountered an error trying to fulfill your request</h3>'+'<p>'+'If the error persists please contact the site maintainer. '+'Thank you for your patience.'+'</p>');jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_ERROR)});var hashquery=Faceted.URLHandler.get();var has_hash=!jQuery.isEmptyObject(hashquery);if(has_hash){Faceted.Query=hashquery}
if(Faceted.Query.b_start===undefined){Faceted.Query.b_start=0}
if(this.mode==='search'&&!has_hash){return}
jQuery(Faceted.Events).trigger(Faceted.Events.QUERY_INITIALIZED);if(!has_hash){Faceted.URLHandler.set()}else{Faceted.URLHandler.hash_changed()}},initialize_paginator: function(){var context=this;Faceted.b_start_changed=false;jQuery('.listingBar a').each(function(i){jQuery(this).click(function(){var href=jQuery(this).attr('href');var regex=new RegExp('b_start\\:int=(\\d+)');var b_start=regex.exec(href)[1];Faceted.b_start_changed=true;context.do_query('b_start',b_start);return false})})},reset: function(evt){Faceted.Query={}},do_query: function(wid,value){if(wid!='b_start'&&!Faceted.b_start_changed){Faceted.Query.b_start=0}
if(!value){value=[]}
if(wid){Faceted.Query[wid]=value}
jQuery(Faceted.Events).trigger(Faceted.Events.FORM_DO_QUERY,{wid:wid});Faceted.URLHandler.set()},do_form_query: function(){var context=this;if(Faceted.Query.b_start===undefined){Faceted.Query.b_start=0}
jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_QUERY_START);context.area.fadeOut('fast', function(){if(Faceted.Options.SHOW_SPINNER){var loading='<div class="faceted_loading"><img src="'+Faceted.BASEURL+'++resource++faceted_images/ajax-loader.gif" /></div>';context.area.html(loading);context.area.fadeIn(Faceted.Options.FADE_SPEED)}
var query=Faceted.SortedQuery();if(context.version){query.version=context.version}
jQuery.get(Faceted.BASEURL+'@@faceted_query',query, function(data){context.area.fadeOut('fast', function(){context.area.html(data);context.area.fadeIn(Faceted.Options.FADE_SPEED);jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_QUERY_SUCCESS)})})})},highlight: function(elements,css_class,remove){for(var i=0;i<elements.length;i++){var element=jQuery('#'+elements[i]);if(remove){jQuery(element).removeClass(css_class)}else{jQuery(element).addClass(css_class)}}},raise_error: function(msg,error_area,highlights){var area=jQuery('#'+error_area);msg='<div class="portalMessage">'+msg+'</div>';area.html(msg);this.highlight(highlights,'error')},clear_errors: function(error_area,highlights){var area=jQuery('#'+error_area);area.html('');this.highlight(highlights,'error',true)}};Faceted.URLHandler={initialize: function(){},hash_changed: function(){Faceted.Query=this.get();jQuery(Faceted.Events).trigger(Faceted.Events.QUERY_CHANGED);Faceted.Form.do_form_query()},document_hash: function(){var r=window.location.href;var i=r.indexOf("#");return(i>=0?r.substr(i+1):'')},get: function(){var hash=jQuery.bbq.getState();var query={};var types=["number","boolean","string"];jQuery.each(hash, function(key,value){var value_type=typeof(value);if(jQuery.inArray(value_type,types)!==-1){value=[value]}
query[key]=value});return query},set: function(query){if(!query){query=Faceted.Query}
query=jQuery.param(query,traditional=true);jQuery.bbq.pushState(query,2)}};Faceted.Sections={initialize: function(){var self=this;self.form=jQuery('.faceted-form');self.advanced=jQuery('.faceted-advanced-widgets',self.form).hide();if(!self.advanced.length){return}
self.buttons=jQuery('.faceted-sections-buttons',self.form);self.more=jQuery('.faceted-sections-buttons-more',self.form).show();self.less=jQuery('.faceted-sections-buttons-less',self.form).hide();jQuery('a',self.buttons).click(function(evt){self.toggle(jQuery(this),evt);return false})},toggle: function(element,evt){this.more.toggle();this.less.toggle();this.advanced.toggle('blind');var tags=jQuery('.faceted-tagscloud-widget:visible',this.form);if(tags.length){jQuery(Faceted.Events).trigger(Faceted.Events.WINDOW_WIDTH_CHANGED)}}};Faceted.AjaxLook={initialize: function(){this.slaves=[];this.locked=false;var js_object=this;jQuery(Faceted.Events).bind(Faceted.Events.AJAX_START, function(evt,data){js_object.add(data.wid)});jQuery(Faceted.Events).bind(Faceted.Events.AJAX_STOP, function(evt,data){js_object.remove(data.wid)});jQuery(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_START, function(evt){js_object.add('faceted-results')});jQuery(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function(evt){js_object.remove('faceted-results')});jQuery(Faceted.Events).bind(Faceted.Events.AJAX_ERROR, function(evt){jQuery(this.slaves).each(function(index){js_object.remove(js_object.slaves[index])})})},add: function(wid){this.lock();this.slaves.push(wid);var widget=jQuery('#'+wid+'_widget');if(widget.length){widget.addClass('faceted-widget-loading')}},remove: function(wid){if(this.slaves.length){this.slaves=jQuery.map(this.slaves, function(slave,index){if(slave==wid){return null}
return slave})}
var widget=jQuery('#'+wid+'_widget');if(widget.length){widget.removeClass('faceted-widget-loading')}
this.unlock()},lock: function(){if(this.locked){return}
this.locked=true;jQuery.each(Faceted.Widgets, function(key){this.widget.addClass('faceted-widget-locked')});var overlay=jQuery('<div>');overlay.addClass('faceted-lock-overlay');overlay.addClass('ui-widget-overlay');overlay.css('z-index',1001);jQuery('#faceted-form').append(overlay)},unlock: function(){if(this.slaves.length){return}
this.locked=false;jQuery.each(Faceted.Widgets, function(key){this.widget.removeClass('faceted-widget-locked')});jQuery('.faceted-lock-overlay').remove()}};Faceted.Load=function(evt,baseurl){if(baseurl){Faceted.BASEURL=baseurl}
jQuery('.faceted-widget:has(div.faceted-widget-error)').remove();jQuery(Faceted.Events).bind(Faceted.Events.REDRAW, function(){if(jQuery('#faceted-left-column:has(div.faceted-widget)').length){jQuery('#center-content-area').addClass('left-area-js')}else{jQuery('#center-content-area').removeClass('left-area-js')}
if(jQuery('#faceted-right-column:has(div.faceted-widget)').length){jQuery('#center-content-area').addClass('right-area-js')}else{jQuery('#center-content-area').removeClass('right-area-js')}});jQuery(Faceted.Events).trigger(Faceted.Events.REDRAW);jQuery(Faceted.Events).trigger(Faceted.Events.INITIALIZE);jQuery(window).bind(Faceted.Events.HASHCHANGE, function(evt){Faceted.URLHandler.hash_changed()});jQuery(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_SUCCESS, function(evt){Faceted.Form.initialize_paginator()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){Faceted.Form.reset()});Faceted.Window.initialize();Faceted.Sections.initialize();Faceted.AjaxLook.initialize();Faceted.Form.initialize();if(window.Calendar){Calendar.prototype.callCloseHandler=function(){if(this.onClose){this.onClose(this)}
this.hideShowCovered();var wid=this.params.inputField.id;wid=wid.split('_')[2];if(!wid){return false}
var widget=Faceted.Widgets[wid];widget.do_query();return false}}};Faceted.Unload=function(){};Faceted.Cleanup=function(){Faceted.Events.cleanup();Faceted.Widgets={};Faceted.Query={};Faceted.URLHandler.set()};(function(jQuery){jQuery.fn.collapsible=function(settings){var self=this;self.colapsed=false;var options={maxitems:0,elements:'li',events:{refresh:'widget-refresh',expand:'widget-expand',colapse:'widget-colapse'},handle_refresh: function(evt,data){jQuery(options.elements,self).show();self.button.hide();if(!options.maxitems){return}
var elements=jQuery(options.elements,self);if(elements.length<options.maxitems){return}
if(self.colapsed){jQuery('a',self.button).text('More')}else{jQuery('a',self.button).text('Less')}
self.button.show();if(!self.colapsed){return}
elements.each(function(index){if(index<options.maxitems){jQuery(this).show()}else{jQuery(this).hide()}})},handle_expand: function(evt,data){self.colapsed=false;self.trigger(options.events.refresh)},handle_colapse: function(evt,data){self.colapsed=true;self.trigger(options.events.refresh)},initialize: function(){self.bind(options.events.refresh, function(evt,data){options.handle_refresh(evt,data)});self.bind(options.events.expand, function(evt,data){options.handle_expand(evt,data)});self.bind(options.events.colapse, function(evt,data){options.handle_colapse(evt,data)});var link=jQuery('<a>').attr('href','#').text('More');self.button=jQuery('<div>').addClass('faceted-checkbox-more').append(link).hide();self.append(self.button);link.click(function(){if(self.colapsed){self.trigger(options.events.expand)}else{self.trigger(options.events.colapse)}
return false});if(options.maxitems){link.click()}}};if(settings){jQuery.extend(options,settings)}
options.initialize();return this}})(jQuery);jQuery(document).ready(function(){jQuery('form.faceted-external-search').submit(function(evt){evt.preventDefault();var form=jQuery(this);var action=form.attr('action');var query=form.serialize();window.location.href=action+'#'+query})});Faceted.CheckboxesWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.fieldset=jQuery('.widget-fieldset',this.widget);this.title=jQuery('legend',this.widget).html();this.elements=jQuery('form input[type=checkbox]',this.widget);this.maxitems=parseInt(jQuery('span',this.widget).text(),10);this.operatorElem=this.widget.find('.faceted-operator a');this.operatorVisible=this.operatorElem.length?true:false;if(this.operatorVisible){this.operator=this.operatorElem.data('value');this.operatorElem.click(function(evt){evt.preventDefault();self.operator_click(this,evt)});this.operatorElem.text(this.operatorElem.data(this.operator))}else{this.operator=this.widget.data('operator')}
this.selected=[];this.version='';var version=jQuery('#faceted-version');if(version){this.version=version.text()}
jQuery('form',this.widget).submit(function(){return false});var self=this;this.elements.click(function(evt){self.checkbox_click(this,evt)});var selected=this.widget.find('form input[type=checkbox]:checked');if(selected.length){this.selected=selected;Faceted.Query[this.wid]=[];selected.each(function(){Faceted.Query[self.wid].push(jQuery(this).val())})}
if(this.operatorVisible){Faceted.Query[self.wid+'-operator']=self.operator}
if(this.maxitems){this.fieldset.collapsible({maxitems:this.maxitems,elements:'li:not(.faceted-checkbox-item-zerocount)'})}
jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){self.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){self.reset()});if(this.widget.hasClass('faceted-count')){var sortcountable=this.widget.hasClass('faceted-sortcountable');jQuery(Faceted.Events).bind(Faceted.Events.QUERY_INITIALIZED, function(evt){self.count(sortcountable)});jQuery(Faceted.Events).bind(Faceted.Events.FORM_DO_QUERY, function(evt,data){if(self.operator!='and'&&(data.wid==self.wid||data.wid=='b_start')){return}
self.count(sortcountable)})}};Faceted.CheckboxesWidget.prototype={checkbox_click: function(element,evt){this.do_query(element)},operator_click: function(element,evt){var self=this;if(self.operator==='or'){self.operator='and';self.operatorElem.text(self.operatorElem.data('and'))}else{self.operator='or';self.operatorElem.text(self.operatorElem.data('or'))}
Faceted.Form.do_query(this.wid+'-operator',self.operator)},operator_label: function(){if(!this.operatorVisible){return ''}
var label=this.widget.find('.faceted-operator label');label=label.length?label.text():'';label+=' '+this.operatorElem.data(this.operator);return '('+label+')'},do_query: function(element){this.selected=jQuery('form input[type=checkbox]:checked',this.widget);var value=[];this.selected.each(function(i){value.push(jQuery(this).val())});Faceted.Form.do_query(this.wid,value)},reset: function(){this.selected=[];jQuery(this.elements).attr('checked',false)},synchronize: function(){this.elements.attr('checked',false);var checked=Faceted.Query[this.wid];if(checked){jQuery('form input[type=checkbox]',this.widget).val(checked);this.selected=jQuery('form input[type=checkbox]:checked',this.widget)}
var operator=Faceted.Query[this.wid+'-operator'];if(this.operatorVisible&&operator){operator=operator[0];this.operator=operator;this.operatorElem.data('value',operator);this.operatorElem.text(this.operatorElem.data(this.operator))}},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+' '+this.operator_label()+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var widget=this;var html=jQuery('<dd>');html.attr('id','criteria_'+this.wid+'_entries');widget.selected.each(function(i){var span=jQuery('<span class="faceted-checkbox-criterion">');var element=jQuery(this);var id=element.attr('id');var value=element.val();var label=jQuery('label[for='+id+']',widget.widget);var title=label.attr('title');label=label.text();var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+id);link.attr('title','Remove '+title+' filter');link.click(function(evt){widget.criteria_remove(value,element);return false});span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span)});return html},criteria_remove: function(value,element){if(!value){this.elements.attr('checked',false);this.do_query()}else{element.attr('checked',false);this.do_query()}},count: function(sortcountable){var query=Faceted.SortedQuery();query.cid=this.wid;if(this.version){query.version=this.version}
if(this.operator&&!query[this.wid+'-operator']){query[this.wid+'-operator']=this.operator}
var context=this;jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_START,{wid:context.wid});jQuery.getJSON(Faceted.BASEURL+'@@faceted_counter',query, function(data){context.count_update(data,sortcountable);jQuery(Faceted.Events).trigger(Faceted.Events.DO_UPDATE);jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_STOP,{wid:context.wid})})},count_update: function(data,sortcountable){var context=this;var lis=jQuery('li',context.widget);jQuery(lis).each(function(){var li=jQuery(this);li.removeClass('faceted-checkbox-item-disabled');li.removeClass('faceted-checkbox-item-zerocount');var input=jQuery('input',li);input.unbind();var key=input.val();var span=jQuery('span',li);if(!span.length){var label=jQuery('label',li);label.append(' ');label.append(jQuery('<span>'));span=jQuery('span',li)}
var value=data[key];value=value?value:0;span.text('('+data[key]+')');if(sortcountable){li.data('count',value)}
if(!value){li.addClass('faceted-checkbox-item-disabled');if(context.widget.hasClass('faceted-zero-count-hidden')){li.addClass('faceted-checkbox-item-zerocount')}
input.attr('disabled','disabled')}else{input.attr('disabled',false);input.click(function(evt){context.checkbox_click(this,evt)})}});if(sortcountable){lis.detach().sort(function(x,y){var a=jQuery(x).data('count');var b=jQuery(y).data('count');return b-a})}
jQuery('ul',context.widget).append(lis);context.fieldset.trigger('widget-refresh')}};Faceted.initializeCheckboxesWidget=function(evt){jQuery('div.faceted-checkboxes-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.CheckboxesWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeCheckboxesWidget)});Faceted.SortingWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+this.wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.reverse=jQuery('#'+this.wid+'_reversed');this.elements=jQuery('option',this.widget);this.selected=[];this.select=jQuery('#'+this.wid);var error=jQuery('.faceted-widget:has(div.faceted-sorting-errors)');if(error.length){error.remove();jQuery(Faceted.Events).trigger(Faceted.Events.REDRAW);return}
jQuery('form',this.widget).submit(function(){return false});var js_widget=this;this.select.change(function(evt){js_widget.select_change(this,evt)});this.reverse.click(function(evt){js_widget.reverse_change(this,evt)});var value=this.select.val();if(value){this.selected=jQuery('option[value="'+value+'"]',this.widget);Faceted.Query[this.wid]=[value];var reverse=this.reverse.attr('checked');if(reverse){Faceted.Query.reversed='on'}}
jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(){js_widget.reset()})};Faceted.SortingWidget.prototype={select_change: function(element,evt){this.do_query(element)},reverse_change: function(element,evt){this.do_query(element)},do_query: function(element){if(!element){this.selected=[];Faceted.Form.do_query(this.wid,[]);return}
var value=null;if(jQuery(element).attr('type')=='checkbox'){value=jQuery(element).attr('checked')?'on':[];if(!this.selected.length){Faceted.Query.reversed=value;return}
Faceted.Form.do_query('reversed',value);return}else{value=jQuery(element).val();if(!value){this.selected=[];value=[]}else{this.selected=jQuery('option[value="'+value+'"]',this.widget)}
Faceted.Form.do_query(this.wid,value);return}},reset: function(reversed){reversed=reversed?true:false;this.select.val("");this.reverse.attr('checked',reversed);this.selected=[]},synchronize: function(){var value=Faceted.Query[this.wid];var reversed_value=Faceted.Query.reversed;if(!reversed_value){reversed_value=false}
else if(reversed_value.length==1&&!reversed_value[0]){reversed_value=false}
else{reversed_value=true}
if(!value){this.reset(reversed_value);return}
var context=this;jQuery.each(value, function(){var selected=jQuery('option[value="'+value+'"]',this.widget);if(!selected.length){context.reset(reversed_value)}else{context.selected=selected;context.select.val(value);context.reverse.attr('checked',reversed_value)}})},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var widget=this;var html=jQuery('<dd>');var span=jQuery('<span class="faceted-sorting-criterion">');html.attr('id','criteria_'+this.wid+'_entries');var element=jQuery(this.selected);var value=element.val();var label=element.html();var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid+'_'+value);link.attr('title','Remove '+label+' filter');link.click(function(evt){widget.criteria_remove();return false});span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span);if(this.reverse.attr('checked')){var rid=this.reverse.attr('id');var rlabel=jQuery('label[for='+rid+']').html();html.append('<span>('+rlabel+')</span>')}
return html},criteria_remove: function(){this.select.val('');this.reverse.attr('checked',false);this.do_query()}};Faceted.initializeSortingWidget=function(evt){jQuery('div.faceted-sorting-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.SortingWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeSortingWidget)});Faceted.TextWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.selected=[];this.button=jQuery('input[type=submit]',this.widget);var js_widget=this;jQuery('form',this.widget).submit(function(){js_widget.text_change(js_widget.button);return false});var input=jQuery('#'+this.wid);var value=input.val();if(value){this.selected=input;Faceted.Query[this.wid]=[value]}
jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset()})};Faceted.TextWidget.prototype={text_change: function(element,evt){this.do_query(element);jQuery(element).removeClass("submitting")},do_query: function(element){var input=jQuery('#'+this.wid);var value=input.val();value=value?[value]:[];if(!element){this.selected=[];return Faceted.Form.do_query(this.wid,[])}
this.selected=[input];var where=jQuery('input[type=radio]:checked',this.widget);where=where.length==1?where.val():'all';if(where=='all'){return Faceted.Form.do_query(this.wid,value)}
var current=Faceted.Query[this.wid];current=current?current:[];if(value.length&&!(value[0] in current)){current.push(value[0])}
return Faceted.Form.do_query(this.wid,current)},reset: function(){this.selected=[];jQuery('#'+this.wid).val('')},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset();return}
var input=jQuery('#'+this.wid);input.attr('value',value);this.selected=[input]},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var widget=this;var html=jQuery('<dd>');var elements=Faceted.Query[this.wid];elements=elements?elements:[];jQuery.each(elements, function(){var label=this.toString();if(label.length>0){var span=jQuery('<span class="faceted-text-criterion">');var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+widget.wid+'_'+label);link.attr('title','Remove '+label+' filter');link.click(function(evt){widget.criteria_remove(label);return false});span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span)}});return html},criteria_remove: function(value){jQuery('#'+this.wid).val('');if(!value){this.selected=[];this.do_query();return}
jQuery('#'+this.wid+'_place_current',this.widget).attr('checked',true);var element=jQuery('input[type=text]',this.widget);var current=Faceted.Query[this.wid];var index=jQuery.inArray(value,current);if(index==-1){return}
current.splice(index,1);Faceted.Query[this.wid]=current;this.do_query(element)}};Faceted.initializeTextWidget=function(evt){jQuery('div.faceted-text-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.TextWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeTextWidget)});Faceted.DateRangeWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.start=jQuery('input[name=start]',this.widget);this.yearRange=jQuery('input[name=calYearRange]',this.widget).val();this.end=jQuery('input[name=end]',this.widget);this.selected=[];this.usePloneFormat=jQuery('input[name=usePloneFormat]',this.widget).val();this.usePloneFormat=this.usePloneFormat=="True"?true:false;this.dateFormat=jQuery('input[name=dateFormat]',this.widget).val();this.language=jQuery('input[name=language]',this.widget).val();var start=this.start.val();var end=this.end.val();if(start&&end){this.selected=[this.start,this.end];Faceted.Query[this.wid]=[start,end]}
var js_widget=this;this.start.datepicker({changeMonth:true,changeYear:true,dateFormat:this.dateFormat,yearRange:this.yearRange,onSelect: function(date,cal){js_widget.force_range();js_widget.select_change(js_widget.start)}});this.end.datepicker({changeMonth:true,changeYear:true,yearRange:this.yearRange,dateFormat:this.dateFormat,onSelect: function(date,cal){js_widget.select_change(js_widget.end)}});if(start){js_widget.force_range()}
this.start.change(function(){var start=js_widget.start.val();var end=js_widget.end.val();if(!start&&!end){js_widget.reset();Faceted.Form.do_query(js_widget.wid,[])}});this.end.change(function(){var start=js_widget.start.val();var end=js_widget.end.val();if(!start&&!end){js_widget.reset();Faceted.Form.do_query(js_widget.wid,[])}});jQuery('form',this.widget).submit(function(){return false});jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset()})};Faceted.DateRangeErrorMsg='Invalid date range';Faceted.DateRangeWidget.prototype={select_change: function(element){this.do_query(element)},force_range: function(){var start_date=this.start.datepicker("getDate");if(!start_date){return}
this.end.datepicker("option","minDate",start_date)},do_query: function(element){var start=this.start.val();var end=this.end.val();if(!start&&!end){this.reset();Faceted.Form.do_query(this.wid,[])}
if(!start||!end){this.selected=[];return false}
var value=[start,end];var start_date;var end_date;if(this.usePloneFormat){start_date=$.datepicker.parseDate(this.dateFormat,start);end_date=$.datepicker.parseDate(this.dateFormat,end)}else{start_date=new Date(start.replace(/-/g,'/'));end_date=new Date(end.replace(/-/g,'/'))}
if(end_date<start_date){Faceted.Form.raise_error(Faceted.DateRangeErrorMsg,this.wid+'_errors',[])}else{this.selected=[this.start,this.end];Faceted.Form.clear_errors(this.wid+'_errors',[]);Faceted.Form.do_query(this.wid,value)}},reset: function(){this.selected=[];this.start.val('');this.end.val('');this.end.datepicker("option","minDate",null)},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset();return false}
if(!value.length){this.reset();return false}
if(value.length<2){this.reset();return false}
var start=value[0];var end=value[1];var start_date;var end_date;if(this.usePloneFormat){start_date=$.datepicker.parseDate(this.dateFormat,start);end_date=$.datepicker.parseDate(this.dateFormat,end)}else{start_date=new Date(start.replace(/-/g,'/'));end_date=new Date(end.replace(/-/g,'/'))}
if(!start_date.getFullYear()){this.reset();return false}
if(!end_date.getFullYear()){this.reset();return false}
this.start.val(start);this.end.val(end);this.selected=[this.start,this.end]},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var widget=this;var html=jQuery('<dd>');html.attr('id','criteria_'+this.wid+'_entries');var start=this.start.val();var end=this.end.val();var start_date;var end_date;if(this.usePloneFormat){start_date=$.datepicker.parseDate(this.dateFormat,start);end_date=$.datepicker.parseDate(this.dateFormat,end)}else{start_date=new Date(start.replace(/-/g,'/'));end_date=new Date(end.replace(/-/g,'/'))}
var label=this.criteria_label(start_date,end_date);var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid+'_');link.attr('title','Remove '+label+' filter');link.click(function(evt){widget.criteria_remove();return false});var span=jQuery('<span class="faceted-daterange-criterion">');span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span);return html},criteria_label: function(start_date,end_date){if(this.usePloneFormat){var options={weekday:"short",year:"numeric",month:"short",day:"numeric"};var start_date_label=start_date.toLocaleDateString(this.language,options);var end_date_label=end_date.toLocaleDateString(this.language,options);return start_date_label+' - '+end_date_label}else{return start_date.toDateString()+' - '+end_date.toDateString()}},criteria_remove: function(){this.reset();return Faceted.Form.do_query(this.wid,[])}};Faceted.initializeDateRangeWidget=function(evt){jQuery('div.faceted-daterange-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.DateRangeWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeDateRangeWidget)});Faceted.AlphabeticalWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.letters=jQuery('#'+wid+' span');this.selected=[];this.version='';var version=jQuery('#faceted-version');if(version){this.version=version.text()}
var selected=jQuery('.faceted_letter_selected');if(selected.length){Faceted.Query[this.wid]=[selected.attr('id').split('-')[1]];this.synchronize()}
var js_widget=this;this.letters.click(function(evt){js_widget.letter_click(this,evt)});jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset()});if(this.widget.hasClass('faceted-count')){var sortcountable=this.widget.hasClass('faceted-sortcountable');jQuery(Faceted.Events).bind(Faceted.Events.QUERY_INITIALIZED, function(evt){js_widget.count(sortcountable)});jQuery(Faceted.Events).bind(Faceted.Events.FORM_DO_QUERY, function(evt,data){if(data.wid==js_widget.wid||data.wid=='b_start'){return}
js_widget.count(sortcountable)})}};Faceted.AlphabeticalWidget.prototype={letter_click: function(letter,evt){this.do_query(letter)},letter_unselect: function(letter){jQuery(letter).removeClass('faceted_letter_selected');this.selected=[]},letter_select: function(letter){this.letter_unselect(this.letters);jQuery(letter).addClass('faceted_letter_selected');if(jQuery(letter).attr('id').split('-')[1]!='all'){this.selected=[letter]}},do_query: function(letter){var value=jQuery(letter).attr('id').split('-')[1];var selected_value='';if(this.selected.length){selected_value=jQuery(this.selected[0]).attr('id').split('-')[1]}
if(value==selected_value){this.letter_select(jQuery('#'+this.wid+'-all'),this.widget);value=[]}else{this.letter_select(letter)}
Faceted.Form.do_query(this.wid,value)},reset: function(){this.letter_select(jQuery('#'+this.wid+'-all',this.widget))},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset()}else{var letter=jQuery('#'+this.wid+'-'+value[0]);if(letter.length){this.letter_select(letter[0])}else{this.reset()}}},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove(this,evt);return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var label=jQuery(this.selected[0]).attr('id').split('-')[1];var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid+'_'+label);link.attr('title','Remove '+label+' filter');var widget=this;link.click(function(evt){widget.criteria_remove(this,evt);return false});var html=jQuery('<dd>');html.attr('id','criteria_'+this.wid+'_entries');var span=jQuery('<span class="faceted-alphabetic-criterion">');span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span);return html},criteria_remove: function(element,evt){this.do_query(this.selected[0])},count: function(sortcountable){var query=Faceted.SortedQuery();query.cid=this.wid;if(this.version){query.version=this.version}
var context=this;jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_START,{wid:context.wid});jQuery.getJSON(Faceted.BASEURL+'@@faceted_counter',query, function(data){context.count_update(data,sortcountable);jQuery(Faceted.Events).trigger(Faceted.Events.DO_UPDATE);jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_STOP,{wid:context.wid})})},count_update: function(data,sortcountable){var context=this;context.letters.each(function(){var letter=jQuery(this);letter.removeClass('faceted-alphabetic-letter-disabled');letter.unbind();var key=letter.attr('id').split('-')[1];var value=data[key];value=value?value:0;letter.attr('title',value);if(sortcountable){letter.data('count',value)}
if(!value){letter.addClass('faceted-alphabetic-letter-disabled')}else{letter.click(function(evt){context.letter_click(this,evt)})}});if(sortcountable){context.letters.detach().sort(function(x,y){var a=jQuery(x).data('count');var b=jQuery(y).data('count');return b-a})}
jQuery('#'+context.wid,context.widget).append(context.letters)}};Faceted.initializeAlphabeticalWidget=function(evt){jQuery('div.faceted-alphabetic-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.AlphabeticalWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeAlphabeticalWidget)});Faceted.TagsCloudWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.tags=jQuery('li',this.widget);this.faceted_count=this.widget.hasClass('faceted-count');this.selected=[];this.version='';var version=jQuery('#faceted-version');if(version){this.version=version.text()}
this.config={};this.initialize();var selected=jQuery('.faceted-tag-selected',this.widget);if(selected.length){var value=selected.attr('id').replace(this.wid,'');value=value.replace(/_-_/g,' ');Faceted.Query[this.wid]=[value];this.synchronize()}
var js_widget=this;this.tags.click(function(evt){js_widget.tag_click(this,evt)});jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset()});jQuery(Faceted.Events).bind(Faceted.Events.QUERY_INITIALIZED, function(evt){js_widget.count()});jQuery(Faceted.Events).bind(Faceted.Events.FORM_DO_QUERY, function(evt,data){if(data.wid==js_widget.wid||data.wid=='b_start'){return}
js_widget.count()});jQuery(Faceted.Events).bind(Faceted.Events.WINDOW_WIDTH_CHANGED, function(evt,data){var width=js_widget.widget.width();jQuery('ul',js_widget.widget).width(width-30);js_widget.update()})};Faceted.TagsCloudWidget.prototype={initialize: function(){var cloud=jQuery('#'+this.wid+'-cloud',this.widget).text();cloud=cloud?cloud:'list';var sizemin=jQuery('#'+this.wid+'-sizemin',this.widget).text();sizemin=parseInt(sizemin,10);sizemin=sizemin?sizemin:10;var sizemax=jQuery('#'+this.wid+'-sizemax',this.widget).text();sizemax=parseInt(sizemax,10);sizemax=sizemax?sizemax:20;var colormin=jQuery('#'+this.wid+'-colormin',this.widget).text();var colormax=jQuery('#'+this.wid+'-colormax',this.widget).text();var height=jQuery('#'+this.wid+'-height',this.widget).text();height=parseInt(height,10);height=height?height:200;height=(cloud=='list')?'auto':height;this.config={type:cloud,sizemin:sizemin,sizemax:sizemax,height:height,colormin:colormin,colormax:colormax};this.update()},update: function(){jQuery('#'+this.wid,this.widget).tagcloud(this.config)},tag_click: function(tag,evt){this.do_query(tag)},unselect: function(tag){jQuery(tag).removeClass('faceted-tag-selected');this.selected=[]},select: function(tag){this.unselect(this.tags);jQuery(tag).addClass('faceted-tag-selected');if(jQuery(tag).attr('id').replace(this.wid,'')!='all'){this.selected=[tag]}},do_query: function(tag){var value=jQuery(tag).attr('id').replace(this.wid,'');value=value.replace(/_-_/g,' ');var selected_value='';if(this.selected.length){selected_value=jQuery(this.selected[0]).attr('id').replace(this.wid,'');selected_value=selected_value.replace(/_-_/g,' ')}
if(value==selected_value){this.select(jQuery('#'+this.wid+'all',this.widget));value=[]}else{this.select(tag)}
Faceted.Form.do_query(this.wid,value)},reset: function(){this.select(jQuery('#'+this.wid+'all',this.widget))},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset()}else{value=value[0].replace(/ /g,'_-_');var tag=jQuery('#'+this.wid+value,this.widget);if(tag.length){this.select(tag[0])}}},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove(this,evt);return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var tag_id=jQuery(this.selected[0]).attr('id');var label=jQuery(this.selected[0]).attr('title');var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+tag_id);link.attr('title','Remove '+label+' filter');var widget=this;link.click(function(evt){widget.criteria_remove(this,evt);return false});var html=jQuery('<dd>');var span=jQuery('<span class="faceted-tagscloud-criterion">');html.attr('id','criteria_'+this.wid+'_entries');span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span);return html},criteria_remove: function(tag,evt){this.do_query(this.selected[0])},count: function(){var query=Faceted.SortedQuery();query.cid=this.wid;if(this.version){query.version=this.version}
var context=this;jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_START,{wid:context.wid});jQuery.get(Faceted.BASEURL+'@@tagscloud_counter',query, function(data){context.count_update(data);jQuery(Faceted.Events).trigger(Faceted.Events.DO_UPDATE);jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_STOP,{wid:context.wid})})},count_update: function(data){var js_widget=this;var all_id=js_widget.wid+'all';var fieldset=jQuery('fieldset',jQuery(data));js_widget.widget.html(fieldset);var min=10000;jQuery('li',js_widget.widget).each(function(){var tag=jQuery(this);var val=tag.attr('value');val=parseInt(val,10);if(val<min&&val>0){min=val}});var all_tag=jQuery('#'+all_id,js_widget.widget);var all=all_tag.attr('value');all_tag.attr('value',min);js_widget.tags=jQuery('li',this.widget);js_widget.tags.click(function(evt){js_widget.tag_click(this,evt)});if(!js_widget.faceted_count){js_widget.update();return}
js_widget.tags.each(function(){var tag=jQuery(this);var html=tag.text();var value=parseInt(tag.attr('value'),10);if(tag.attr('id')==all_id){value=all}else{value-=1}
html=html.replace(/\s\(\d+\)/,'');html+=' ('+value+')';tag.html(html);tag.unbind();if((tag.attr('value')===1)&&(tag.attr('id')!=all_id)){tag.addClass('faceted-tag-disabled')}else{tag.removeClass('faceted-tag-disabled');tag.click(function(evt){js_widget.tag_click(this,evt)})}});js_widget.update()}};Faceted.initializeTagsCloudWidget=function(evt){jQuery('div.faceted-tagscloud-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.TagsCloudWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeTagsCloudWidget)});Faceted.AutocompleteWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.selected=[];this.button=jQuery('input[type=submit]',this.widget);var js_widget=this;jQuery('form',this.widget).submit(function(){js_widget.text_change(js_widget.button);return false});var input=jQuery('#'+this.wid);var value=input.val();if(value){this.selected=input;Faceted.Query[this.wid]=[value]}
jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset()})};Faceted.AutocompleteWidget.prototype={text_change: function(element,evt){this.do_query(element);jQuery(element).removeClass("submitting")},do_query: function(element){var input=jQuery('#'+this.wid);var value=input.val();value=value?[value]:[];if(!element){this.selected=[];return Faceted.Form.do_query(this.wid,[])}
this.selected=[input];var where=jQuery('input[type=radio]:checked',this.widget);where=where.length==1?where.val():'all';if(where=='all'){return Faceted.Form.do_query(this.wid,value)}
var current=Faceted.Query[this.wid];current=current?current:[];if(value.length&&!(value[0] in current)){current.push(value[0])}
return Faceted.Form.do_query(this.wid,current)},reset: function(){this.selected=[];jQuery('#'+this.wid).val('')},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset();return}
var input=jQuery('#value_'+this.wid);input.attr('value',value);this.selected=[input]},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var widget=this;var html=jQuery('<dd>');var elements=Faceted.Query[this.wid];elements=elements?elements:[];jQuery.each(elements, function(){var label=this.toString();if(label.length>0){var span=jQuery('<span class="faceted-autocomplete-criterion">');var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+widget.wid+'_'+label);link.attr('title','Remove '+label+' filter');link.click(function(evt){widget.criteria_remove(label);return false});span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span)}});return html},criteria_remove: function(value){jQuery('#'+this.wid).val('');if(!value){this.selected=[];this.do_query();return}
jQuery('#'+this.wid+'_place_current',this.widget).attr('checked',true);var element=jQuery('input[type=text]',this.widget);var current=Faceted.Query[this.wid];var index=jQuery.inArray(value,current);if(index==-1){return}
current.splice(index,1);Faceted.Query[this.wid]=current;this.do_query(element)}};Faceted.initializeAutocompleteWidget=function(evt){jQuery('div.faceted-autocomplete-widget').each(function(){var wid=jQuery(this).attr('id');var autocomplete_view=jQuery(this).attr('data-autocomplete-view');var multiple=(jQuery(this).attr('data-multiple')==='true');var placeholder=jQuery(this).attr('data-placeholder');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.AutocompleteWidget(wid);jQuery("#"+wid).select2({placeholder:placeholder,multiple:multiple,allowClear:true,minimumInputLength:2,ajax:{url:autocomplete_view,delay:250,dataType:'json',params:{global:false},data: function(term,page){return{term:term,add_terms:true}},results: function(data,page){return{results:data}},cache:false}})})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeAutocompleteWidget)});Faceted.DebugWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.query_area=jQuery('dd.debug-query pre',this.widget);this.after_area=jQuery('dd.debug-after pre',this.widget);this.config_area=jQuery('dd.debug-config pre',this.widget);this.count_area=jQuery('dd.debug-count pre',this.widget);jQuery('dd',this.widget).hide();jQuery('dt',this.widget).each(function(){var dt=jQuery(this);var css=dt.attr('class');var parent=dt.parent('dl');var minmax=jQuery('<span>').addClass('ui-icon ui-icon-plus').css('float','left');minmax.click(function(){var button=jQuery(this);jQuery('dd.'+css,parent).toggle();if(button.hasClass('ui-icon-minus')){button.removeClass('ui-icon-minus');button.addClass('ui-icon-plus')}else{button.removeClass('ui-icon-plus');button.addClass('ui-icon-minus')}});dt.prepend(minmax)});var js_widget=this;jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()})};Faceted.DebugWidget.prototype={synchronize: function(){var context=this;var query=jQuery.extend({},Faceted.Query);query['debugger']=this.wid;jQuery.get(Faceted.BASEURL+'@@faceted.widget.debug.query',query, function(data){if(data=="[]"){jQuery('.debug-query',context.widget).hide()}else{jQuery('dt.debug-query',context.widget).show()}
context.query_area.text(data)});jQuery.get(Faceted.BASEURL+'@@faceted.widget.debug.after',query, function(data){if(data=="[]"){jQuery('.debug-after',context.widget).hide()}else{jQuery('dt.debug-after',context.widget).show()}
context.after_area.text(data)});jQuery.get(Faceted.BASEURL+'@@faceted.widget.debug.criteria',query, function(data){if(data=="[]"){jQuery('.debug-config',context.widget).hide()}else{jQuery('dt.debug-config',context.widget).show()}
context.config_area.text(data)});jQuery.get(Faceted.BASEURL+'@@faceted.widget.debug.counters',query, function(data){if(data=="[]"){jQuery('.debug-count',context.widget).hide()}else{jQuery('dt.debug-count',context.widget).show()}
context.count_area.text(data)})},criteria: function(){return []}};Faceted.initializeDebugWidget=function(evt){jQuery('div.faceted-debug-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.DebugWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeDebugWidget)});Faceted.RangeWidget=function(wid){var js_widget=this;this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.start=jQuery('input[name=start]',this.widget);this.end=jQuery('input[name=end]',this.widget);this.selected=[];var start=this.start.val();var end=this.end.val();if(start&&end){this.selected=[this.start,this.end];Faceted.Query[this.wid]=[start,end]}
jQuery('form',this.widget).submit(function(){return false});var handle=function(evt){js_widget.select_change(this,evt)};this.start.change(handle);this.end.change(handle);jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset()})};Faceted.RangeWidget.prototype={select_change: function(element){this.do_query(element)},do_query: function(element){var start=this.start.val();var end=this.end.val();if(!start||!end){this.selected=[];return false}
var value=[start,end];if(end<start){var msg='Invalid range';Faceted.Form.raise_error(msg,this.wid+'_errors',[])}else{this.selected=[this.start,this.end];Faceted.Form.clear_errors(this.wid+'_errors',[]);Faceted.Form.do_query(this.wid,value)}},reset: function(){this.selected=[];this.start.val('');this.end.val('')},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset();return false}
if(!value.length){this.reset();return false}
if(value.length<2){this.reset();return false}
var start=value[0];var end=value[1];this.start.val(start);this.end.val(end);this.selected=[this.start,this.end]},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var widget=this;var html=jQuery('<dd>');var span=jQuery('<span class="faceted-range-criterion">');var start=this.start.val();var end=this.end.val();var label=start+' - '+end;var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid+'_');link.attr('title','Remove '+label+' filter');link.click(function(evt){widget.criteria_remove();return false});span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span);return html},criteria_remove: function(){this.reset();return Faceted.Form.do_query(this.wid,[])}};Faceted.initializeRangeWidget=function(evt){jQuery('div.faceted-range-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.RangeWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeRangeWidget)});Faceted.RadioWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.fieldset=jQuery('.widget-fieldset',this.widget);this.title=jQuery('legend',this.widget).html();this.elements=jQuery('input[type=radio]',this.widget);this.maxitems=parseInt(jQuery('span',this.widget).text(),10);this.selected=[];this.version='';var version=jQuery('#faceted-version');if(version){this.version=version.text()}
jQuery('form',this.widget).submit(function(){return false});var js_widget=this;this.elements.click(function(evt){js_widget.radio_click(this,evt)});var selected=jQuery('input[type=radio]:checked',this.widget);if(selected.length){this.selected=selected;Faceted.Query[this.wid]=[this.selected.val()]}
jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(){js_widget.reset()});if(this.widget.hasClass('faceted-count')){var sortcountable=this.widget.hasClass('faceted-sortcountable');jQuery(Faceted.Events).bind(Faceted.Events.QUERY_INITIALIZED, function(evt){js_widget.count(sortcountable)});jQuery(Faceted.Events).bind(Faceted.Events.FORM_DO_QUERY, function(evt,data){if(data.wid==js_widget.wid||data.wid=='b_start'){return}
js_widget.count(sortcountable)})}
if(this.maxitems){this.fieldset.collapsible({maxitems:this.maxitems,elements:'li:not(.faceted-radio-item-zerocount)'})}};Faceted.RadioWidget.prototype={radio_click: function(element,evt){if(!jQuery(element).val()){element=null}
this.do_query(element)},do_query: function(element){if(!element){this.selected=[];return Faceted.Form.do_query(this.wid,[])}else{this.selected=[element];var value=jQuery(this.selected[0]).val();return Faceted.Form.do_query(this.wid,value)}},reset: function(){jQuery(this.elements[0]).attr('checked',true);this.selected=[]},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset();return}
var context=this;if(typeof value!='object'){value=[value]}
jQuery.each(value, function(){var radio=jQuery('#'+context.wid+'_widget input[type=radio][value="'+this+'"]');if(!radio.length){context.reset()}else{context.selected=radio;context.selected.attr('checked',true)}})},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var widget=this;var html=jQuery('<dd>');html.attr('id','criteria_'+this.wid+'_entries');var element=jQuery(this.selected);var id=element.attr('id');var label=jQuery('label[for='+id+']');var title=label.attr('title');label=label.text();var link=jQuery('<a href="#">[X]</a>');var span=jQuery('<span class="facted-radio-criterion">');link.attr('id','criteria_'+id);link.attr('title','Remove '+title+' filter');link.click(function(evt){widget.criteria_remove();return false});span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span);return html},criteria_remove: function(){var element=jQuery(this.elements[0]);element.attr('checked',true);this.do_query()},count: function(sortcountable){var query=Faceted.SortedQuery();query.cid=this.wid;if(this.version){query.version=this.version}
var context=this;jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_START,{wid:context.wid});jQuery.getJSON(Faceted.BASEURL+'@@faceted_counter',query, function(data){context.count_update(data,sortcountable);jQuery(Faceted.Events).trigger(Faceted.Events.DO_UPDATE);jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_STOP,{wid:context.wid})})},count_update: function(data,sortcountable){var context=this;var lis=jQuery('li',context.widget);jQuery(lis).each(function(){var li=jQuery(this);li.removeClass('faceted-radio-item-disabled');li.removeClass('faceted-radio-item-zerocount');var input=jQuery('input',li);input.unbind();var key=input.val();var span=jQuery('span',li);if(!span.length){var label=jQuery('label',li);label.append(' ');label.append(jQuery('<span>'));span=jQuery('span',li)}
var value=data[key];value=value?value:0;span.text('('+value+')');if(sortcountable){li.data('count',value)}
if(!value){li.addClass('faceted-radio-item-disabled');if(context.widget.hasClass('faceted-zero-count-hidden')){li.addClass('faceted-radio-item-zerocount')}
input.attr('disabled','disabled')}else{input.attr('disabled',false);input.click(function(evt){context.radio_click(this,evt)})}});if(sortcountable){lis.detach().sort(function(x,y){var a=jQuery(x).data('count');var b=jQuery(y).data('count');return b-a})}
jQuery('ul',context.widget).append(lis);context.fieldset.trigger('widget-refresh')}};Faceted.initializeRadioWidget=function(evt){jQuery('div.faceted-radio-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.RadioWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeRadioWidget)});Faceted.CriteriaWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.title=jQuery('legend',this.widget).html();this.area=jQuery('#'+wid);this.reset_button=jQuery('#'+wid+'_reset');this.toggle_button=jQuery('.faceted-criteria-hide-show',this.widget);this.toggle_button_count=jQuery('.faceted-criteria-count',this.toggle_button);var js_widget=this;this.reset_button.click(function(evt){js_widget.reset_click(this,evt);return false});var toggle_buttons=jQuery('a',this.toggle_button);toggle_buttons.click(function(evt){js_widget.toggle_button_click(this,evt);return false});js_widget.initialize_syndication();jQuery(Faceted.Events).bind(Faceted.Events.AJAX_QUERY_START, function(evt){return js_widget.update()});jQuery(Faceted.Events).bind(Faceted.Events.DO_UPDATE, function(evt){return js_widget.update()});jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){return js_widget.update_syndication()})};Faceted.CriteriaWidget.prototype={reset_click: function(element,evt){jQuery(Faceted.Events).trigger(Faceted.Events.RESET);this.do_query()},toggle_button_click: function(element,evt){this.area.toggle('blind');jQuery('a',this.toggle_button).toggle();this.toggle_button_count.toggle()},do_query: function(wid,value){Faceted.Form.do_query(wid,value)},update: function(){var context=this;var empty=true;context.widget.fadeOut('fast', function(){context.area.empty();jQuery.each(Faceted.Query, function(key){var widget=Faceted.Widgets[key];if(!widget){return}
var criteria=widget.criteria();jQuery.each(criteria, function(){context.area.append(this);empty=false})});var count=jQuery('dd span',context.area).length;context.toggle_button_count.text('('+count+')');if(!empty){context.widget.fadeIn('fast')}})},criteria: function(){return []},initialize_syndication: function(){this.rss=null;this.rss_href='';this.skos=null;this.skos_href='';var icon=null;var rss=jQuery('#document-action-rss, #document-action-rss2').find('a');if(rss.length){rss=jQuery(rss[0]).clone();icon=jQuery('img',rss);icon.attr('id',icon.attr('id')+'-'+this.wid);rss.addClass('faceted-criteria-syndication-rss');rss.attr('id',this.wid+'syndication-rss');jQuery('.faceted-criteria-reset',this.widget).prepend(rss);this.rss=jQuery('#'+this.wid+'syndication-rss',this.widget);this.rss_href=rss.attr('href')}
var skos=jQuery('#document-action-skos').find('a');if(skos.length){skos=jQuery(skos[0]).clone();icon=jQuery('img',skos);icon.attr('id',icon.attr('id')+'-'+this.wid);skos.addClass('faceted-criteria-syndication-skos');skos.attr('id',this.wid+'syndication-skos');jQuery('.faceted-criteria-reset',this.widget).prepend(skos);this.skos=jQuery('#'+this.wid+'syndication-skos',this.widget);this.skos_href=this.skos.attr('href')}},update_syndication: function(){var hash='ajax=True&';hash+=Faceted.URLHandler.document_hash();if(this.rss){this.rss.attr('href',this.rss_href+'?'+hash)}
if(this.skos){this.skos.attr('href',this.skos_href+'?'+hash)}}};Faceted.initializeCriteriaWidget=function(evt){jQuery('div.faceted-criteria-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.CriteriaWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeCriteriaWidget)});Faceted.DateWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.select_from=jQuery('select[name=from]',this.widget);this.select_to=jQuery('select[name=to]',this.widget);this.select_from.hide();this.select_to.hide();var js_widget=this;this.slider=jQuery('select',this.widget).selectToUISlider({labels:2,labelSrc:'text',sliderOptions:{change: function(){js_widget.change()}}});jQuery('span.ui-slider-label',this.widget).each(function(i){if(i!==11){return}
var span=jQuery(this);span.addClass('ui-slider-label-show')});this.selected=[];var from=this.select_from.val();var to=this.select_to.val();if((from!=='now-past')||(to!=='now_future')){this.selected=[this.select_from,this.select_to];Faceted.Query[this.wid]=[from,to]}
jQuery('form',this.widget).submit(function(){return false});jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset_ui()})};Faceted.DateWidget.prototype={change: function(){var from=this.select_from.val();var to=this.select_to.val();if(from==='now-past'&&to==='now_future'){this.reset();Faceted.Form.do_query(this.wid,[])}else{this.do_query()}},do_query: function(){var value=[this.select_from.val(),this.select_to.val()];this.selected=[this.select_from,this.select_to];Faceted.Form.do_query(this.wid,value)},reset: function(){this.selected=[];this.select_from.val('now-past');this.select_to.val('now_future')},reset_ui: function(){this.reset();this.select_from.trigger('change');this.select_to.trigger('change')},synchronize: function(){var q_value=Faceted.Query[this.wid];if(!q_value){this.reset_ui();return}
if(!q_value.length){this.reset_ui();return}
if(q_value.length<2){this.reset_ui();return}
this.select_from.val(q_value[0]).trigger('change');this.select_to.val(q_value[1]).trigger('change')},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var from=jQuery('option:selected',this.select_from).text();var to=jQuery('option:selected',this.select_to).text();var label=from+' - '+to;var widget=this;var html=jQuery('<dd>');html.attr('id','criteria_'+this.wid+'_entries');var span=jQuery('<span class="faceted-date-criterion">');var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid+'_');link.attr('title','Remove '+label+' filter');link.click(function(evt){widget.criteria_remove();return false});span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span);return html},criteria_remove: function(){this.reset_ui();return Faceted.Form.do_query(this.wid,[])}};Faceted.initializeDateWidget=function(evt){jQuery('div.faceted-date-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.DateWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeDateWidget)});Faceted.ResultsPerPageWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+this.wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.elements=jQuery('option',this.widget);this.select=jQuery('#'+this.wid);this.selected=[];jQuery('form',this.widget).submit(function(){return false});var js_widget=this;this.select.change(function(evt){js_widget.select_change(this,evt)});var value=this.select.val();if(value){this.selected=jQuery('option[value="'+value+'"]',this.widget);Faceted.Query[this.wid]=[value]}
jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset()})};Faceted.ResultsPerPageWidget.prototype={select_change: function(element,evt){if(!jQuery(element).val()){element=null}
this.do_query(element)},do_query: function(element){if(!element){this.selected=[];return Faceted.Form.do_query(this.wid,[])} else{var value=jQuery(element).val();this.selected=jQuery('#'+this.wid+'_widget option[value="'+value+'"]');return Faceted.Form.do_query(this.wid,value)}},reset: function(){this.select.val("");this.selected=[]},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset();return}
var context=this;jQuery.each(value, function(){var selected=jQuery('#'+context.wid+'_widget option[value="'+value+'"]');if(!selected.length){context.reset()} else{context.selected=selected;context.select.val(value)}})},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var widget=this;var html=jQuery('<dd>');var span=jQuery('<span class="faceted-resultsperpage-criterion">');html.attr('id','criteria_'+this.wid+'_entries');var element=jQuery(this.selected);var value=element.val();var label=element.html();var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid+'_'+value);link.attr('title','Remove '+label+' filter');link.click(function(evt){widget.criteria_remove();return false});span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span);return html},criteria_remove: function(){this.select.val('');this.do_query()}};Faceted.initializeResultsPerPageWidget=function(evt){jQuery('div.faceted-resultsperpage-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.ResultsPerPageWidget(wid)})};jQuery(document).ready(
function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeResultsPerPageWidget)});var FacetedTree={version:'2.0'};FacetedTree.Events={};FacetedTree.Events.CHANGED='FACETEDTREE-CHANGED';FacetedTree.Events.AJAX_START='FACETEDTREE-AJAX-START';FacetedTree.Events.AJAX_STOP='FACETEDTREE-AJAX-STOP';FacetedTree.JsTree=function(wid,container,mode){this.BASEURL='';if(window.FacetedEdit){this.BASEURL=FacetedEdit.BASEURL}else if(window.Faceted){this.BASEURL=Faceted.BASEURL}
this.wid=wid;this.mode=mode||'view';this.input=jQuery('#'+wid,container);this.input.attr('readonly','readonly');this.theme=jQuery('#'+wid+'-theme',container);this.area=jQuery('<div>');this.area.addClass('tree');this.area.text('Loading...');this.area.hide();this.area.width(this.input.width());this.input.after(this.area);var js_tree=this;this.input.click(function(evt){js_tree.show()});jQuery(document).click(function(e){var target=jQuery(e.target);if(target.is('#'+js_tree.input.attr('id'))){return}
var parent=target.parents('#'+js_tree.area.attr('id'));if(parent.length){return}
js_tree.hide()});jQuery(document).keydown(function(e){if(e.keyCode==27){js_tree.hide()}});var query={};query.cid=this.wid;query.mode=this.mode;jQuery(FacetedTree.Events).trigger(FacetedTree.Events.AJAX_START,{msg:'Loading ...'});jQuery.getJSON(js_tree.BASEURL+'@@faceted.path.tree.json',query, function(data){if(data.length){js_tree.initialize(data)}else{if(mode=='edit'){jQuery('form',container).hide();jQuery('div.faceted-path-errors',container).show()}else{jQuery('.faceted-widget:has(div.faceted-path-errors)').remove();jQuery(Faceted.Events).trigger(Faceted.Events.REDRAW)}}
jQuery(FacetedTree.Events).trigger(FacetedTree.Events.AJAX_STOP,{msg:data})})};FacetedTree.JsTree.prototype={initialize: function(static_tree){var js_tree=this;js_tree.area.tree({ui:{theme_name:js_tree.theme.attr('title'),theme_path:js_tree.theme.text()},types:{"default":{clickable:true,renameable:false,deletable:false,creatable:false,draggable:false}},data:{type:'json',async:true,opts:{method:'POST',url:js_tree.BASEURL+'@@faceted.path.tree.json'}},callback:{beforedata: function(node,tree){if(node===false){tree.settings.data.opts['static']=static_tree;return}
tree.settings.data.opts['static']=false;var data={cid:js_tree.wid};data.mode=js_tree.mode;if(node){data.path=node.attr('path')}
return data},onselect: function(node,tree){js_tree.change(node,tree)}}})},show: function(){this.area.show()},hide: function(){this.area.hide()},change: function(node,tree){this.hide();node=jQuery(node);var value=node.attr('path');if(this.input.val()==value){value=''}
this.input.val(value);jQuery(FacetedTree.Events).trigger(FacetedTree.Events.CHANGED,{path:value})}};Faceted.PathWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.input=jQuery('input',this.widget);this.breadcrumbs=jQuery('<dd>');this.selected=[];var value=this.input.val();if(value){this.selected=this.input;Faceted.Query[this.wid]=[value]}
var tree=new FacetedTree.JsTree(this.wid,this.widget);var js_widget=this;jQuery('form',this.widget).submit(function(){return false});jQuery(FacetedTree.Events).bind(FacetedTree.Events.CHANGED, function(data){js_widget.text_change(js_widget.input)});jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset()})};Faceted.PathWidget.prototype={text_change: function(element,evt){this.do_query(element)},do_query: function(element){var value=this.input.val();value=value?[value]:[];if(!element){this.selected=[];return Faceted.Form.do_query(this.wid,[])}
this.selected=[this.input];return Faceted.Form.do_query(this.wid,value)},reset: function(){this.selected=[];this.input.val('')},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset();return}
this.selected=[this.input]},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var js_widget=this;js_widget.breadcrumbs.text('Loading...');var query={};query.path=js_widget.input.val();query.cid=js_widget.wid;jQuery.getJSON(Faceted.BASEURL+'@@faceted.path.breadcrumbs.json',query, function(data){js_widget.breadcrumbs.empty();jQuery.each(data, function(){js_widget.breadcrumbs.append(jQuery('<span>').html('&raquo;'));var a=jQuery('<a>');a.attr('href',this.url);a.attr('title',this.title);a.text(this.title);a.click(function(){var path=jQuery(this).attr('href');js_widget.input.val(path);jQuery(FacetedTree.Events).trigger(FacetedTree.Events.CHANGED,{path:path});return false});js_widget.breadcrumbs.append(a)})});return js_widget.breadcrumbs},criteria_remove: function(){this.selected=[];this.input.val('');this.do_query()}};Faceted.initializePathWidget=function(evt){jQuery('div.faceted-path-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.PathWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializePathWidget)});Faceted.SelectWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+this.wid+'_widget');this.widget.show();this.title=jQuery('legend',this.widget).html();this.elements=jQuery('option',this.widget);this.select=jQuery('#'+this.wid);this.selected=[];this.version='';var version=jQuery('#faceted-version');if(version){this.version=version.text()}
jQuery('form',this.widget).submit(function(){return false});var js_widget=this;this.select.change(function(evt){js_widget.select_change(this,evt)});var value=this.select.val();if(value){this.selected=jQuery('option[value="'+value+'"]',js_widget.widget);Faceted.Query[this.wid]=[value]}
jQuery(Faceted.Events).bind(Faceted.Events.QUERY_CHANGED, function(evt){js_widget.synchronize()});jQuery(Faceted.Events).bind(Faceted.Events.RESET, function(evt){js_widget.reset()});if(this.widget.hasClass('faceted-count')){var sortcountable=this.widget.hasClass('faceted-sortcountable');jQuery(Faceted.Events).bind(Faceted.Events.QUERY_INITIALIZED, function(evt){js_widget.count(sortcountable)});jQuery(Faceted.Events).bind(Faceted.Events.FORM_DO_QUERY, function(evt,data){if(data.wid==js_widget.wid||data.wid=='b_start'){return}
js_widget.count(sortcountable)})}};Faceted.SelectWidget.prototype={select_change: function(element,evt){if(!jQuery(element).val()){element=null}
this.do_query(element)},do_query: function(element){if(!element){this.selected=[];return Faceted.Form.do_query(this.wid,[])}else{var value=jQuery(element).val();this.selected=jQuery('#'+this.wid+'_widget option[value="'+value+'"]');return Faceted.Form.do_query(this.wid,value)}},reset: function(){this.select.val("");this.selected=[]},synchronize: function(){var value=Faceted.Query[this.wid];if(!value){this.reset();return}
var context=this;jQuery.each(value, function(){var selected=jQuery('option[value="'+value+'"]',context.widget);if(!selected.length){context.reset()}else{context.selected=selected;context.select.val(value)}})},criteria: function(){var html=[];var title=this.criteria_title();var body=this.criteria_body();if(title){html.push(title)}
if(body){html.push(body)}
return html},criteria_title: function(){if(!this.selected.length){return ''}
var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid);link.attr('title','Remove '+this.title+' filters');var widget=this;link.click(function(evt){widget.criteria_remove();return false});var html=jQuery('<dt>');html.attr('id','criteria_'+this.wid+'_label');html.append(link);html.append('<span>'+this.title+'</span>');return html},criteria_body: function(){if(!this.selected.length){return ''}
var widget=this;var html=jQuery('<dd>');var span=jQuery('<span class="facted-select-criterion">');html.attr('id','criteria_'+this.wid+'_entries');var element=jQuery(this.selected);var value=element.val();var label=element.attr('title');var link=jQuery('<a href="#">[X]</a>');link.attr('id','criteria_'+this.wid+'_'+value);link.attr('title','Remove '+label+' filter');link.click(function(evt){widget.criteria_remove();return false});span.append(link);jQuery('<span>').text(label).appendTo(span);html.append(span);return html},criteria_remove: function(){this.select.val('');this.do_query()},count: function(sortcountable){var query=Faceted.SortedQuery();query.cid=this.wid;if(this.version){query.version=this.version}
var context=this;jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_START,{wid:context.wid});jQuery.getJSON(Faceted.BASEURL+'@@faceted_counter',query, function(data){context.count_update(data,sortcountable);jQuery(Faceted.Events).trigger(Faceted.Events.DO_UPDATE);jQuery(Faceted.Events).trigger(Faceted.Events.AJAX_STOP,{wid:context.wid})})},count_update: function(data,sortcountable){var context=this;var select=jQuery('select',context.widget);var options=jQuery('option',context.widget);var current_val=select.val();jQuery(options).each(function(){var option=jQuery(this);option.removeClass('faceted-select-item-disabled');option.attr('disabled',false);var key=option.val();var value=data[key];value=value?value:0;var option_txt=option.attr('title');option_txt+=' ('+value+')';option.html(option_txt);if(sortcountable){option.data('count',value)}
if(!value){option.attr('disabled','disabled');option.addClass('faceted-select-item-disabled')}});if(sortcountable){options.detach().sort(function(x,y){var a=jQuery(x).data('count');var b=jQuery(y).data('count');return b-a});select.append(options);select.val(current_val)}}};Faceted.initializeSelectWidget=function(evt){jQuery('div.faceted-select-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];Faceted.Widgets[wid]=new Faceted.SelectWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializeSelectWidget)});Faceted.PortletWidget=function(wid){this.wid=wid;this.widget=jQuery('#'+wid+'_widget');this.widget.show();jQuery('legend',this.widget).hide();jQuery('fieldset',this.widget).css('border','none');jQuery('form',this.widget).submit(function(){return true})};Faceted.initializePortletWidget=function(evt){jQuery('div.faceted-portlet-widget').each(function(){var wid=jQuery(this).attr('id');wid=wid.split('_')[0];var widget=new Faceted.PortletWidget(wid)})};jQuery(document).ready(function(){jQuery(Faceted.Events).bind(Faceted.Events.INITIALIZE,Faceted.initializePortletWidget)});
