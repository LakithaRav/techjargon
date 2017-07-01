
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

});
