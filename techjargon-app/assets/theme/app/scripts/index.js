$(function () {
  var typed = $('#txt-search').typed({
    strings: ['sample', 'sample2', 'sample3'],
    typeSpeed: 100,
    startDelay: 10,
    shuffle: true,
    loop: true,
    loopCount: null,
    showCursor: false,
    backSpeed: 0,
    backDelay: 1800
  });

  $('#txt-search').on('click', function () {
    $(this).data('typed').reset();
    $(this).attr('placeholder', 'Search')
    $(this).val(null);
  });
  
  // Add VueJS
  // var app = new Vue({
  //   el: '#app',
  //   data: {
  //     message: 'Hello Vue!'
  //   }
  // });
  search.init('#searchNavbar');
});

var search = {
  hasOpened: false,
  init: function (el) {
    var self = this;
    $(el).find('button').on('click', function () {
      if (!self.hasOpened) {
        self.openSearch($(el).find('input'));
        self.hasOpened = true;
      } else {
        // Go to search screen logic
      }
    })
  },
  openSearch: function (el) {
    $(el).animate({width: 300, opacity: 1}, 200, function () {
      $(this).focus();
    });
  }
};