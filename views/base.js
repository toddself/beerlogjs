'use strict';

var lodash = require('lodash');
var Backbone = require('backbone');
var $ = require('jquery');
// var transformFunctions = require('../utils/transforms');

Backbone.$ = $;

var BaseView = Backbone.View.extend({});

var viewOpts = {
	events: {
		input: this._inputBinder,
		textarea: this._inputBinder,
		select: this._inputBinder
	},

	_inputBinder: function(evt){
		var dataKey = this.$(evt.currentTarget).data('store');
		var ignore = this.$(evt.currentTarget).data('ignore');
		var transforms = this.$(evt.currentTarget).data('transforms');
		var value = this.$(evt.currentTarget).val() || this.$(evt.currentTarget + ' option:selected');
		if(!ignore && this.model){
			if(transforms){
				transforms.split(',').forEach(function(trans){
					if(typeof tranformFunctions[trans] === 'function'){
						value = transformFunctions[trans].call(this, value);
					}
				});
			}
			this.model.set(dataKey, value);
		} 
	}
}

function extend(){
	var args = Array.prototype.slice.call(arguments);
	var dest = viewOpts;
	args.forEach(function(src){
		if(typeof src === 'object'){
			Object.keys(src).forEach(function(key){
				if(typeof dest[key] === 'object'){
					dest[key] = lodash.assign(dest[key], src[key]);
				} else if(dest[key] === 'function' && src[key] === 'function'){
					var destFunc = dest[key];
					var srcFunc = src[key];
					var newFunc = function(){
						destFunc.apply(BaseView, arguments);
						srcFunc.apply(Baseview, arguments);
					}
					dest[key] = newFunc;
				} else {
					desk[key] = src[key];
				}
			});
		}
	});

  return BaseView.extend(dest);
};

module.exports = extend;