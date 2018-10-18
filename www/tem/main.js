function fetch(url, method, cb, data) {
  const req = new XMLHttpRequest();
  method = method || 'GET';
  req.open(method, url);
  req.timeout = 5000;
  req.ontimeout = function() {
    console.log('网络链接超时，请检查网络或者设置更长的超时时间');
  };
  req.onerror = function networkError() {
    console.log('网络链接错误');
  };
  req.onprogress = function(){};
  req.onreadystatechange = function() {
    if (req.readyState !== 4) return;
    if (req.status >= 200 && req.status < 300) {
      cb(req.responseText);
    } else {
      console.log('资源不存在或其他网络原因', req.status);
    }
  };
  req.send(data || '');
}
function nothing() {}
function getPrevSiblings(elem, filter) {
  var sibs = [];
  while(elem = elem.previousSibling){
    if(elem.nodeType == 3) continue;
    if(!filter || filter(elem)) sibs.push(elem);
  }
  return sibs;
}
if (document.readyState == 'loading') {
  console.log('hello');
  const addTagEl = document.getElementById('add_tag');
  const modal = document.getElementById('modal');
  const modalClose = document.getElementById('modal-close');
  const cls = modal.classList;
  modalClose.addEventListener('click', function(){
    modal.classList.remove('modal-show');
  })

  function onAddTagClick(e) {
    e.preventDefault();
    if (cls.contains('modal-show')) {
      cls.remove('modal-show');
    }else{
      cls.add('modal-show');
    }
  }
  function onAddTagSubmit() {
    const bid = document.getElementById('bookid').textContent;
    const content = document.getElementById('input-content').textContent;
    fetch('/book/' + bid + '/tag', 'POST',nothing, content);
    cls.remove('modal-show');
  }
  addTagEl.addEventListener('click', onAddTagClick);
  const postComment = document.getElementById('post-comment');
  postComment.addEventListener('submit', onAddTagSubmit);

  const addCommentEl = document.getElementById('add_comment');
  addCommentEl.addEventListener('click', onAddTagClick);

  const addRateEl = document.getElementById('add_rate');
  function onAddRate(e) {
    e.preventDefault();
    const el = e.target;
    if (el.nodeName = 'li') {
      let total = addRateEl.getElementsByTagName('li');
      for (var i = 0, len = total.length; i < len; i++) {
        total[i].classList.remove('like');
      }
      total = getPrevSiblings(el).concat([el])
      total.forEach(function(elem){
        elem.classList.add('like');
      });
      fetch('/url', 'POST', function(){});
    }
  }
  addRateEl.addEventListener('click', onAddRate);

  const postCommentForm = document.getElementById('post-comment');
  postCommentForm.addEventListener('submit', function(e){
    e.preventDefault();
  })
}

