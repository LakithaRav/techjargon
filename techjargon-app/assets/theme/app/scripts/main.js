console.log('\'Allo \'Allo!');
$(function () {
  // Article list hover effect
  $('.article-list a').mouseenter(function () {
    $(this).parent().parent().find('a').not(this).css('opacity', '0.2');
  }).mouseleave(function () {
    $('.article-list a').css('opacity', '1');
  });
});
