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
});
