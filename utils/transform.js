'use strict';

exports.toDate = function(dateStr){
  var d = new Date(dateStr);
  if(!isNaN(d)){
    return d.toISOString();
  } else {
    return undefined;
  }
};