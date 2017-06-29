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
});

function scrollTo(attr) {
  $('html, body').animate({
    scrollTop: $(attr).offset().top - 70
  }, 500);
}
