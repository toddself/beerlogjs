'use strict';

var BaseView = require('./views/base');

var View = BaseView({events: {test: this._inputBinder}});
var v = new View();
console.log(v.events);