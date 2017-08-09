$(function () {
  $('#tags').selectize({
    plugins: ['remove_button'],
    delimiter: ',',
    copyClassesToDropdown: true,
    persist: false,
    create: true,
    options: [],
    valueField: 'name',
    labelField: 'name',
    searchField: 'name'
  });
  $('#meta').selectize({
    create: true,
    options: [
      {value: 'home', text: 'home'},
      {value: 'wiki', text: 'wiki'},
      {value: 'url', text: 'url'},
      {value: 'github', text: 'github'},
      {value: 'video', text: 'video'},
      {value: 'other', text: 'other'}
    ],
    items: [
      'home'
    ]
  });

  $('#content').typeProgress();
});
