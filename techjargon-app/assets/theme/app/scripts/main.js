console.log('\'Allo \'Allo!');
$(document).ready(function () {
  // Article list hover effect
  $('.article-list a').mouseenter(function () {
    $(this).parent().parent().find('a').not(this).css('opacity', '0.2');
  }).mouseleave(function () {
    $('.article-list a').css('opacity', '1');
  });

  // Rating stars
  $('#articleRatings').barrating({
    theme: 'fontawesome-stars-o',
    initialRating: 3,
    readonly: true
  });
  $('#rateArticle').barrating({
    theme: 'fontawesome-stars-o',
    initialRating: 0,
  });

  headerSeachBar.init('#searchNavbar');

  $('#share').jsSocials({
    showLabel: false,
    shares: ['email', 'twitter', 'facebook', 'googleplus', 'linkedin']
  });
});

function scrollTo(attr) {
  $('html, body').animate({
    scrollTop: $(attr).offset().top - 70
  }, 500);
}

// Open search bar
var headerSeachBar = {
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
    $(el).animate({
      width: 400,
      opacity: 1
    }, 200, function () {
      $(this).focus();
    });
  }
};

// Search dropdown
var search = function (el) {
  $(el).selectize({
    valueField: 'url',
    labelField: 'name',
    searchField: 'name',
    create: false,
    render: {
      option: function (item, escape) {
        return '<div>' +
          '<span class="title">' +
          '<span class="name"><i class="icon ' + (item.fork ? 'fork' : 'source') + '"></i>' + escape(item.name) + '</span>' +
          '<span class="by">' + escape(item.username) + '</span>' +
          '</span>' +
          '<span class="description">' + escape(item.description) + '</span>' +
          '<ul class="meta">' +
          (item.language ? '<li class="language">' + escape(item.language) + '</li>' : '') +
          '<li class="watchers"><span>' + escape(item.watchers) + '</span> watchers</li>' +
          '<li class="forks"><span>' + escape(item.forks) + '</span> forks</li>' +
          '</ul>' +
          '</div>';
      }
    }
  });
}
