'use strict';

var lodash = require('lodash');
var Backbone = require('backbone');
var $ = require('jquery');
var transformFunctions = require('../utils/transforms');

Backbone.$ = $;

/**
 * @namespace BaseView
 */
var BaseView = Backbone.View.extend({});

// this is wrapped in a function just so we can turn off the possible strict
// violation warning from jshint
var viewOpts = function(){
  /* jshint validthis:true */
  return {
    events: {
      input: this._inputHandler,
      textarea: this._inputHandler,
      select: this._inputHandler
    },

    /**
     * Simple one-way data binding for reading from the DOM into an attached model
     * @private
     * @method  _inputHandler
     * @param  {object} evt The event object from jquery
     * @return {object} undefined
     */
    _inputHandler: function(evt){
      var dataKey = this.$(evt.currentTarget).data('store');
      var ignore = this.$(evt.currentTarget).data('ignore');
      var transforms = this.$(evt.currentTarget).data('transforms');
      var value = this.$(evt.currentTarget).val() || this.$(evt.currentTarget + ' option:selected');
      if(!ignore && this.model){
        if(transforms){
          transforms.split(',').forEach(function(trans){
            if(typeof transformFunctions[trans] === 'function'){
              value = transformFunctions[trans].call(this, value);
            }
          });
        }
        this.model.set(dataKey, value);
      }
    }
  };
};

/**
 * Create our own version of extend to allow for multiple `events` arrays
 * to be defined and still inherit the parent. Also allows for merging functions
 * @method  extend
 * @memberOf  BaseView
 * @param {...object} [obj] A list of objects to combine with the base view options
 * @return {function} a backbone view based on our passed in definition
 */
function extend(){
  var args = Array.prototype.slice.call(arguments);
  var dest = viewOpts();
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
            srcFunc.apply(BaseView, arguments);
          };
          dest[key] = newFunc;
        } else {
          dest[key] = src[key];
        }
      });
    }
  });

  return BaseView.extend(dest);
}

module.exports = {extend: extend};