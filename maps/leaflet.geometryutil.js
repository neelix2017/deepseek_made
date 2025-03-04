(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as an anonymous module.
        define(['leaflet'], factory);
    } else if (typeof module === 'object' && module.exports) {
        // Node/CommonJS
        module.exports = factory(require('leaflet'));
    } else {
        // Browser globals
        root.DraggableLines = factory(root.L);
    }
}(typeof self !== 'undefined' ? self : this, function (L) {

var z = L.Icon;
var Lr = L.Rectangle;
var K = L.Marker;
var A = L.Polygon;
var x = L.Draggable;
var E = L.DomEvent;
var F = L.Handler;
var W = L.Util ;
var q = L.Evented;
var m = L.Polyline;
var k = L.LineUtil;
var Z = L.latLng;	
var u = L;

	
	
var j=Object.defineProperty,J=(s,e,t)=>e in s?j(s,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):s[e]=t,d=(s,e,t)=>J(s,typeof e!="symbol"?e+"":e,t),V=`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="25.1" height="40.227">
	<defs>
		<linearGradient id="b">
			<stop offset="0" stop-color="\${color1}" />
			<stop offset="1" stop-color="\${color2}" />
		</linearGradient>
		<linearGradient id="a">
			<stop offset="0" stop-color="\${color3}" />
			<stop offset="1" stop-color="\${color4}" />
		</linearGradient>
		<linearGradient xlink:href="#a" id="c" gradientUnits="userSpaceOnUse"
			gradientTransform="translate(-432.796 -503.349)" x1="445.301" y1="541.286" x2="445.301" y2="503.72" />
		<linearGradient xlink:href="#b" id="d" gradientUnits="userSpaceOnUse"
			gradientTransform="translate(-341.216 -503.35)" x1="351.748" y1="522.774" x2="351.748" y2="503.721" />
	</defs>
	<path fill="#fff" d="M6.329 4.513h12.625v14.5H6.329z" />
	<path
		d="M12.594.55C6.021.55.55 6.241.55 12.416c0 2.778 1.564 6.308 2.694 8.746l9.306 17.872 9.262-17.872c1.13-2.438 2.738-5.791 2.738-8.746C24.55 6.241 19.167.55 12.594.55zm0 7.155a4.714 4.714 0 0 1 4.679 4.71c0 2.588-2.095 4.663-4.679 4.679-2.584-.017-4.679-2.09-4.679-4.679a4.714 4.714 0 0 1 4.679-4.71z"
		fill="url(#c)" stroke="url(#d)" stroke-width="1.1" stroke-linecap="round" />
	<path
		d="M12.581 1.657c-5.944 0-10.938 5.219-10.938 10.75 0 2.359 1.443 5.832 2.563 8.25l.031.031 8.313 15.969 8.25-15.969.031-.031c1.135-2.448 2.625-5.706 2.625-8.25 0-5.538-4.931-10.75-10.875-10.75zm0 4.969c3.168.021 5.781 2.601 5.781 5.781 0 3.18-2.613 5.761-5.781 5.781-3.168-.02-5.75-2.61-5.75-5.781 0-3.172 2.582-5.761 5.75-5.781z"
		stroke="#fff" stroke-width="1.1" stroke-linecap="round" stroke-opacity=".122" fill="none" />
</svg>`,Y=`<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24">
	<g transform="matrix(.02604 0 0 .02604 1.302 1.302)" fill="none" stroke="#000" opacity="0.3">
		<circle cx="410.9" cy="410.9" r="410.9" color="#000" overflow="visible" stroke-width="100" />
		<path d="M410.9 223.2v375.4M598.6 410.9H223.2" stroke-width="120" stroke-linecap="round" />
	</g>
</svg>`,$="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACkAAAApCAQAAAACach9AAACMUlEQVR4Ae3ShY7jQBAE0Aoz/f9/HTMzhg1zrdKUrJbdx+Kd2nD8VNudfsL/Th///dyQN2TH6f3y/BGpC379rV+S+qqetBOxImNQXL8JCAr2V4iMQXHGNJxeCfZXhSRBcQMfvkOWUdtfzlLgAENmZDcmo2TVmt8OSM2eXxBp3DjHSMFutqS7SbmemzBiR+xpKCNUIRkdkkYxhAkyGoBvyQFEJEefwSmmvBfJuJ6aKqKWnAkvGZOaZXTUgFqYULWNSHUckZuR1HIIimUExutRxwzOLROIG4vKmCKQt364mIlhSyzAf1m9lHZHJZrlAOMMztRRiKimp/rpdJDc9Awry5xTZCte7FHtuS8wJgeYGrex28xNTd086Dik7vUMscQOa8y4DoGtCCSkAKlNwpgNtphjrC6MIHUkR6YWxxs6Sc5xqn222mmCRFzIt8lEdKx+ikCtg91qS2WpwVfBelJCiQJwvzixfI9cxZQWgiSJelKnwBElKYtDOb2MFbhmUigbReQBV0Cg4+qMXSxXSyGUn4UbF8l+7qdSGnTC0XLCmahIgUHLhLOhpVCtw4CzYXvLQWQbJNmxoCsOKAxSgBJno75avolkRw8iIAFcsdc02e9iyCd8tHwmeSSoKTowIgvscSGZUOA7PuCN5b2BX9mQM7S0wYhMNU74zgsPBj3HU7wguAfnxxjFQGBE6pwN+GjME9zHY7zGp8wVxMShYX9NXvEWD3HbwJf4giO4CFIQxXScH1/TM+04kkBiAAAAAElFTkSuQmCC";function H(s){return`data:image/svg+xml;base64,${btoa(s)}`}function ee(s){let e=V;for(let t of Object.keys(s))e=e.replace(new RegExp(`\\$\\{${t}\\}`,"g"),s[t]);return e}function S(s){let e=H(ee(s));return new z.Default({imagePath:new String(""),iconUrl:e,iconRetinaUrl:e,shadowUrl:$})}var b=S({color1:"#2e6c97",color2:"#3883b7",color3:"#126fc6",color4:"#4c9cd1"}),T=S({color1:"#2E9749",color2:"#06EA3F",color3:"#03D337",color4:"#40DD68"}),U=S({color1:"#972E2E",color2:"#B73838",color3:"#C61212",color4:"#D14C4C"}),te=new z({iconUrl:H(Y),iconSize:[24,24],iconAnchor:[12,12]});function y(s,e,...t){return typeof e=="function"?e(s,...t):typeof e=="boolean"?e:Array.isArray(e)?e.includes(s):e===s}function M(s,e,t,i=!1){let r=u.LineUtil.isFlat(e),n=r?[e]:e;if(!n.some(o=>o.length>=2))throw new Error("Line doesn't have any track points.");i&&(n=n.map(o=>[...o,o[0]]));let a=s.getMaxZoom();a===1/0&&(a=s.getZoom());let l=(Array.isArray(t)?t:[t]).map(o=>s.project(o,a)),c=[];for(let o=0;o<n.length;o++){let g,f=s.project(n[o][0],a);for(let p=1;p<n[o].length;p++){g=f,f=s.project(n[o][p],a);for(let _=0;_<l.length;_++){let C=l[_],D=u.LineUtil._sqClosestPointOnSegment(C,g,f,!0);(c[_]==null||D<c[_].sqDist)&&(c[_]={sqDist:D,idx:[o,p-1],point:C,pointA:g,pointB:f})}}}let h=c.map(o=>{let g=u.LineUtil.closestPointOnSegment(o.point,o.pointA,o.pointB),f=o.pointB.distanceTo(o.pointA),p=[o.idx[0],o.idx[1]+(f===0?.5:g.distanceTo(o.pointA)/f)];return{idx:r?p[1]:p,closest:s.unproject(g,a)}});return Array.isArray(t)?h:h[0]}function se(s,e,t,i){let r,n;typeof e[0]=="number"?(r=typeof i=="number"?i:M(s,t,i).idx,n=e):typeof i=="number"?(r=i,n=M(s,t,e).map(a=>a.idx)):[r,...n]=M(s,t,[i,...e]).map(a=>a.idx);for(let a=1;a<n.length;a++)if(n[a]>r)return a;return n.length-1}function le(s,e){return Array.isArray(e)?s[e[0]][e[1]]:s[e]}function N(s,e,t){let i=Array.isArray(t)?t:[t];if(i.length===0)return s;if(i.length===1)return[...s.slice(0,i[0]),e,...s.slice(i[0])];{let r=[...s];return r[i[0]]=N(r[i[0]],e,i.slice(1)),r}}function G(s,e,t){let i=Array.isArray(t)?t:[t];if(i.length===0)return s;if(i.length===1)return[...s.slice(0,i[0]),e,...s.slice(i[0]+1)];{let r=[...s];return r[i[0]]=G(r[i[0]],e,i.slice(1)),r}}function Q(s,e){let t=Array.isArray(e)?e:[e];if(t.length===0)return s;if(t.length===1)return[...s.slice(0,t[0]),...s.slice(t[0]+1)];{let i=[...s];return i[t[0]]=Q(i[t[0]],t.slice(1)),i}}function w(s,e,t,i){if(s instanceof u.Rectangle){let a=Array.isArray(t)?t[1]:t,l=s.getBounds();a===0?s.setBounds(u.latLngBounds([Math.min(e.lat,l.getNorth()),Math.min(e.lng,l.getEast())],l.getNorthEast())):a===1?s.setBounds(u.latLngBounds([Math.max(e.lat,l.getSouth()),Math.min(e.lng,l.getEast())],l.getSouthEast())):a===2?s.setBounds(u.latLngBounds([Math.max(e.lat,l.getSouth()),Math.max(e.lng,l.getWest())],l.getSouthWest())):a===3&&s.setBounds(u.latLngBounds([Math.min(e.lat,l.getNorth()),Math.max(e.lng,l.getWest())],l.getNorthWest()));return}let r=s.hasDraggableLinesRoutePoints(),n=r?s.getDraggableLinesRoutePoints():s.getLatLngs();i?n=N(n,e,t):n=G(n,e,t),r?s.setDraggableLinesRoutePoints(n):s.setLatLngs(n)}function ie(s,e){if(s instanceof u.Rectangle)return;let t=s.hasDraggableLinesRoutePoints(),i=t?s.getDraggableLinesRoutePoints():s.getLatLngs();i=Q(i,e),t?s.setDraggableLinesRoutePoints(i):s.setLatLngs(i)}function re(s,e,t,i){let r=i?e:[...e].reverse(),n=s.latLngToContainerPoint(r[0]),a=r.find((c,h)=>h>0&&n.distanceTo(s.latLngToContainerPoint(c))>0),l;if(!a)l=u.point(n.x+(i?-1:1)*t,n.y);else{let c=s.latLngToContainerPoint(a),h=t/n.distanceTo(c);l=u.point(n.x-h*(c.x-n.x),n.y-h*(c.y-n.y))}return s.containerPointToLatLng(l)}var v=class extends K{constructor(e,t,i,r,n){super(i,n),d(this,"_draggable"),d(this,"_layer"),d(this,"_isInsert"),d(this,"_dragIdx"),d(this,"_dragFrom"),this._draggable=e,this._layer=t,this._isInsert=r}onAdd(e){return super.onAdd(e),this.on("dragstart",this.handleDragStart,this),this.on("drag",this.handleDrag,this),this.on("dragend",this.handleDragEnd,this),this}onRemove(e){return super.onRemove(e),this}handleDragStart(e){let t=this.getLatLng();this._dragFrom=t,this._dragIdx=this.getIdx(),w(this._layer,t,this._dragIdx,this._isInsert),this._draggable.fire("dragstart",{layer:this._layer,from:t,to:t,idx:this._dragIdx,isNew:this._isInsert})}handleDrag(){let e=this.getLatLng();w(this._layer,e,this._dragIdx,!1),this._draggable.fire("drag",{layer:this._layer,from:this._dragFrom,to:e,idx:this._dragIdx,isNew:this._isInsert})}handleDragEnd(){let e={layer:this._layer,from:this._dragFrom,to:this.getLatLng(),idx:this._dragIdx,isNew:this._isInsert};Promise.resolve().then(()=>{w(e.layer,e.to,e.idx,!1),this._draggable.fire("dragend",e)})}},P=class extends v{constructor(e,t,i,r,n,a){super(e,t,i,!1,{draggable:!0,...n}),d(this,"_idx"),d(this,"_removeOnClick"),d(this,"_over",!1),this._idx=r,this._removeOnClick=a}onAdd(e){super.onAdd(e);let t=this._layer.getDraggableLinesRoutePoints()||this._layer.getLatLngs(),i=Array.isArray(this._idx)?t[this._idx[0]]:t;return this._removeOnClick&&!(this._layer instanceof Lr)&&i.length>(this._layer instanceof A?3:2)&&this.on("click",this.handleClick),this.on("mouseover",()=>{x._dragging||(this._over=!0,this._draggable.fire("dragmouseover",{layer:this._layer,idx:this._idx,marker:this}))}),this.on("mouseout",()=>{x._dragging||(this._over=!1,this._draggable.fire("dragmouseout",{layer:this._layer,idx:this._idx,marker:this}))}),this}onRemove(e){return super.onRemove(e),this._over&&this._draggable.fire("dragmouseout",{layer:this._layer,idx:this._idx,marker:this}),this}getIdx(){return this._idx}handleClick(){let e=this.getIdx();ie(this._layer,e),this._draggable.fire("remove",{layer:this._layer,idx:e})}};function ne(s,e){let t=W.create(e),i=t._setIconStyles;return t._setIconStyles=(r,n)=>{i.call(t,r,n);let a=s.options.weight*2;r.style.padding=`${a}px`,r.style.boxSizing="content-box",r.style.marginLeft=`${parseInt(r.style.marginLeft)-a}px`,r.style.marginTop=`${parseInt(r.style.marginTop)-a}px`,r.style.display="none"},t}var I=class extends v{constructor(e,t,i,r){super(e,t,i,!0,{draggable:!0,zIndexOffset:-1e5,...r,icon:ne(t,r.icon)}),d(this,"renderPoint")}onAdd(e){return super.onAdd(e),e.on("mousemove",this.handleMapMouseMove,this),E.on(e.getContainer(),"mouseover",this.handleMapMouseOver,this),this.on("click",this.handleClick,this),this.updateLatLng(this.getLatLng()),this}onRemove(e){return this.isHidden()||this.fireMouseOut(),super.onRemove(e),e.off("mousemove",this.handleMapMouseMove,this),E.off(e.getContainer(),"mouseover",this.handleMapMouseOver,this),this}show(){this._icon.style.display="",this._shadow&&(this._shadow.style.display=""),this.fireMouseOver()}hide(){this._icon.style.display="none",this._shadow&&(this._shadow.style.display="none"),this.fireMouseOut()}isHidden(){return this._icon.style.display=="none"}getIdx(){if(!this.renderPoint)throw new Error("renderPoint is not set");return this.renderPoint.idx}handleClick(){if(!this.renderPoint)return;let e=this.renderPoint.closest,t=this.renderPoint.idx;w(this._layer,e,t,!0),this._draggable.fire("insert",{layer:this._layer,latlng:e,idx:t})}shouldRemove(e){return!this._layer._containsPoint(this._map.latLngToLayerPoint(e))}getRenderPoint(e){let t=M(this._map,this._layer.getLatLngs(),e,this._layer instanceof A);if(this._map.project(e).distanceTo(this._map.project(t.closest))>this._layer.options.weight/2+1)return;let r=this._layer.hasDraggableLinesRoutePoints()?se(this._map,this._draggable._getRoutePointIndexes(this._layer),this._layer.getLatLngs(),t.idx):Array.isArray(t.idx)?[t.idx[0],Math.ceil(t.idx[1])]:Math.ceil(t.idx);return{closest:t.closest,idx:r}}updateLatLng(e){if(x._dragging)return!1;if(this.shouldRemove(e))return this.remove(),!1;this.renderPoint=this.getRenderPoint(e),this.renderPoint&&this.setLatLng(this.renderPoint.closest);let t=!this.isHidden();this.renderPoint&&!t?this.show():!this.renderPoint&&t?this.hide():t&&this.fireMouseMove()}handleMapMouseMove(e){this.updateLatLng(this._map.mouseEventToLatLng(e.originalEvent))}handleMapMouseOver(e){!x._dragging&&e.target!==this.getElement()&&e.target!==this._layer.getElement()&&this.remove()}fireMouseOver(){this._draggable.fire("tempmouseover",{layer:this._layer,idx:this.getIdx(),marker:this,latlng:this.getLatLng()})}fireMouseMove(){this._draggable.fire("tempmousemove",{layer:this._layer,idx:this.getIdx(),marker:this,latlng:this.getLatLng()})}fireMouseOut(){this._draggable.fire("tempmouseout",{layer:this._layer,marker:this})}},R=class extends v{constructor(e,t,i,r,n,a){super(e,t,i,!0,{pane:"overlayPane",zIndexOffset:-2e5,...n}),d(this,"_idx"),d(this,"_tempMarker"),d(this,"_tempMarkerOptions"),this._idx=r,this._tempMarkerOptions=a}onAdd(e){return super.onAdd(e),this.on("mouseover",this.handleMouseOver,this),this}onRemove(e){return super.onRemove(e),this._tempMarker&&(this._tempMarker.remove(),delete this._tempMarker),this}getIdx(){return this._idx}handleMouseOver(e){this._draggable.removeTempMarker(),this._tempMarker=new O(this._draggable,this._layer,this,e.latlng,this.getIdx(),this._tempMarkerOptions).addTo(this._map),this._draggable._tempMarker=this._tempMarker}},O=class extends I{constructor(e,t,i,r,n,a){super(e,t,r,a),d(this,"_plusMarker"),d(this,"_idx"),this._plusMarker=i,this._idx=n}shouldRemove(e){let t=this._map.latLngToLayerPoint(e),i=X.getPosition(this._plusMarker._icon);return Math.abs(i.y-t.y)>this._plusMarker._icon.offsetHeight/2||Math.abs(i.x-t.x)>this._plusMarker._icon.offsetWidth/2}getRenderPoint(){return{idx:this._idx,closest:this.getLatLng()}}fireMouseOver(){this._draggable.fire("plusmouseover",{layer:this._layer,idx:this.getIdx(),marker:this,plusMarker:this._plusMarker})}fireMouseMove(){}fireMouseOut(){this._draggable.fire("plusmouseout",{layer:this._layer,idx:this.getIdx(),marker:this,plusMarker:this._plusMarker})}},B=class extends(()=>{function e(t){F.call(this,t)}return Object.setPrototypeOf(e.prototype,F.prototype),Object.assign(e.prototype,q.prototype),e})(){constructor(e,t){super(e),d(this,"options"),d(this,"_tempMarker"),d(this,"handleLayerAdd",i=>{i.layer instanceof m&&this.shouldEnableForLayer(i.layer)&&this.enableForLayer(i.layer)}),d(this,"handleLayerRemove",i=>{i.layer instanceof m&&this.disableForLayer(i.layer)}),d(this,"handleLayerMouseOver",i=>{x._dragging||this.drawTempMarker(i.target,i.latlng)}),d(this,"handleLayerSetLatLngs",i=>{let r=i.target;(!x._dragging||i.target instanceof Lr)&&(this.removeTempMarker(),r._draggableLines&&(r._draggableLines.routePointIndexes=void 0,this.drawDragMarkers(r),this.drawPlusMarkers(r)))}),this.options={enableForLayer:i=>i.options.interactive,allowDraggingLine:!0,allowExtendingLine:!0,removeOnClick:!0,...t}}addHooks(){this._map.on("layeradd",this.handleLayerAdd),this._map.on("layerremove",this.handleLayerRemove),this._map.eachLayer(e=>{this.handleLayerAdd({layer:e})})}removeHooks(){this._map.off("layeradd",this.handleLayerAdd),this._map.off("layerremove",this.handleLayerRemove),this._map.eachLayer(e=>{this.handleLayerRemove({layer:e})})}shouldEnableForLayer(e){return y(e,this.options.enableForLayer)}drawDragMarkers(e){var t,i,r,n;if(!e._draggableLines)return;if(e instanceof Lr){let h=e.getBounds(),o=[h.getSouthWest(),h.getNorthWest(),h.getNorthEast(),h.getSouthEast()];for(let g=0;g<o.length;g++)e._draggableLines.dragMarkers[g]?e._draggableLines.dragMarkers[g].setLatLng(o[g]):e._draggableLines.dragMarkers[g]=new P(this,e,o[g],g,{icon:b,...(i=(t=this.options).dragMarkerOptions)==null?void 0:i.call(t,e,g,o.length)},!1).addTo(this._map);return}this.removeDragMarkers(e);let a=e.getDraggableLinesRoutePoints()||e.getLatLngs(),l=k.isFlat(a)?[a]:a,c=k.isFlat(a);for(let h=0;h<l.length;h++)for(let o=0;o<l[h].length;o++){let g=c?o:[h,o],f=y(e,this.options.removeOnClick,g),p={icon:e instanceof A?b:o==0?T:o==l[h].length-1?U:b,...(n=(r=this.options).dragMarkerOptions)==null?void 0:n.call(r,e,o,l[h].length)},_=new P(this,e,l[h][o],g,p,f).addTo(this._map);e._draggableLines.dragMarkers.push(_)}}removeDragMarkers(e){if(e._draggableLines){for(let t of e._draggableLines.dragMarkers)t.removeFrom(this._map);e._draggableLines.dragMarkers=[]}}drawPlusMarkers(e){var t,i,r,n;if(this.removePlusMarkers(e),e instanceof A||!e._draggableLines||!y(e,this.options.allowExtendingLine))return;let a=e.getLatLngs(),l=k.isFlat(a)?[a]:a,c=e.getDraggableLinesRoutePoints();for(let h=0;h<l.length;h++)if(!(l[h].length<2))for(let o of[!0,!1]){let g;c?g=o?0:c.length:k.isFlat(a)?g=o?0:l[h].length:g=o?[h,0]:[h,l[h].length];let f={icon:te,...(i=(t=this.options).plusMarkerOptions)==null?void 0:i.call(t,e,o)},p={icon:o?T:U,...(n=(r=this.options).plusTempMarkerOptions)==null?void 0:n.call(r,e,o)},_=new R(this,e,re(this._map,l[h],24+e.options.weight/2,o),g,f,p).addTo(this._map);e._draggableLines.plusMarkers.push(_)}}removePlusMarkers(e){if(e._draggableLines){for(let t of e._draggableLines.plusMarkers)t.removeFrom(this._map);e._draggableLines.plusMarkers=[]}}drawTempMarker(e,t){var i,r;if(this.removeTempMarker(),e instanceof Lr||!y(e,this.options.allowDraggingLine))return;let n={icon:b,...(r=(i=this.options).tempMarkerOptions)==null?void 0:r.call(i,e)};this._tempMarker=new I(this,e,t,n).addTo(this._map)}removeTempMarker(){this._tempMarker&&(this._tempMarker.removeFrom(this._map),delete this._tempMarker)}enableForLayer(e){e._draggableLines||(e._draggableLines={dragMarkers:[],plusMarkers:[],zoomEndHandler:()=>{this.drawPlusMarkers(e)},routePointIndexes:void 0},e.on("mouseover",this.handleLayerMouseOver),e.on("draggableLines-setLatLngs",this.handleLayerSetLatLngs),e.on("draggableLines-setRoutePoints",this.handleLayerSetLatLngs),this._map.on("zoomend",e._draggableLines.zoomEndHandler),this.drawDragMarkers(e),this.drawPlusMarkers(e))}redrawForLayer(e){e._draggableLines&&(this.drawDragMarkers(e),this.drawPlusMarkers(e),this._tempMarker&&this._tempMarker._layer===e&&this.drawTempMarker(e,this._tempMarker.getLatLng()))}disableForLayer(e){e.off("mouseover",this.handleLayerMouseOver),e.off("draggableLines-setLatLngs",this.handleLayerSetLatLngs),e.off("draggableLines-setRoutePoints",this.handleLayerSetLatLngs),e._draggableLines&&this._map.off("zoomend",e._draggableLines.zoomEndHandler),this.removeDragMarkers(e),this.removePlusMarkers(e),delete e._draggableLines}redraw(){this._map.eachLayer(e=>{if(!(e instanceof m))return;let t=this.shouldEnableForLayer(e);e._draggableLines&&!t?this.disableForLayer(e):!e._draggableLines&&t?this.enableForLayer(e):e._draggableLines&&this.redrawForLayer(e)})}_getRoutePointIndexes(e){if(e._draggableLines){if(!e._draggableLines.routePointIndexes){let t=e.getDraggableLinesRoutePoints();if(!t)return;let i=e.getLatLngs();e._draggableLines.routePointIndexes=M(this._map,[i],t).map(r=>r.idx[1])}}else return;return e._draggableLines.routePointIndexes}};m.prototype.hasDraggableLinesRoutePoints=function(){return this instanceof Lr?!1:this.options.draggableLinesRoutePoints!=null};m.prototype.getDraggableLinesRoutePoints=function(){var s;if(!(this instanceof Lr))return(s=this.options.draggableLinesRoutePoints)==null?void 0:s.map(e=>Z(e))};m.prototype.setDraggableLinesRoutePoints=function(s){this instanceof Lr||(this.options.draggableLinesRoutePoints=s,this.fire("draggableLines-setRoutePoints"))};var oe=m.prototype.setLatLngs;m.prototype.setLatLngs=function(...s){let e=oe.apply(this,s);return this.fire("draggableLines-setLatLngs"),e};
//# sourceMappingURL=L.DraggableLines.js.map
/*
	global.L = global.L || {}; // Ensure L object exists
    global.L.DraggableLinesDragMarker = P;
    global.L.DraggableLinesMarker = v;
    global.L.DraggableLinesPlusMarker = R;
    global.L.DraggableLinesPlusTempMarker = O;
    global.L.DraggableLinesTempMarker = I;
    global.L.createDefaultMarkerIcon = S;
    global.L.createDefaultMarkerIconSrc = ee;
    global.L.createSvgDataUrl = H;
    global.L.default = B;
    global.L.defaultIcon = b;
    global.L.endIcon = U;
    global.L.getFromPosition = le;
    global.L.getPlusIconPoint = re;
    global.L.getRouteInsertPosition = se;
    global.L.insertAtPosition = N;
    global.L.locateOnLine = M;
    global.L.matchesLayerFilter = y;
    global.L.plusIcon = te;
    global.L.removeFromPosition = Q;
    global.L.removePoint = ie;
    global.L.setPoint = w;
    global.L.startIcon = T;
    global.L.updateAtPosition = G;
	*/
return B; // B is the class name for DraggableLines
}));