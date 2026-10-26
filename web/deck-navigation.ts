(function(){
  var chapters = document.querySelectorAll<HTMLElement>('article[id^="ch"]');
  var railItems = document.querySelectorAll<HTMLElement>('.rail__item');
  var progressFill = document.querySelector<HTMLElement>('.progress-bar__fill');
  var topbarNum = document.querySelector('.topbar__meta strong');
  var mobileBtn = document.querySelector('.mobile-chapter');
  var mobileNum = document.querySelector('.mobile-chapter__num');

  var chapterTitles: Record<string, string> = {};
  chapters.forEach(function(ch){
    var t = ch.querySelector('.chapter-title');
    chapterTitles[ch.id] = t ? (t.textContent || '').replace(/\s+/g,' ').trim() : ch.id;
  });
  chapterTitles['ch01'] = 'Cover';

  function update(){
    // Progress bar
    var maxScroll = document.documentElement.scrollHeight - window.innerHeight;
    var pct = maxScroll > 0 ? Math.min(100, (window.scrollY / maxScroll) * 100) : 0;
    if(progressFill) progressFill.style.width = pct + '%';

    // Active chapter — first chapter whose top is above 30% of viewport
    var trigger = window.innerHeight * 0.3;
    var activeId = chapters[0] ? chapters[0].id : null;
    chapters.forEach(function(ch){
      var r = ch.getBoundingClientRect();
      if(r.top < trigger) activeId = ch.id;
    });
    if(!activeId) return;
    var num = activeId.replace('ch','');

    railItems.forEach(function(item){
      var link = item.querySelector('a');
      var match = link && link.getAttribute('href') === '#' + activeId;
      item.classList.toggle('rail__item--active', !!match);
    });
    if(topbarNum) topbarNum.textContent = num;
    if(mobileNum) mobileNum.textContent = num;
    if(mobileBtn){
      // Replace text content after the num span
      var nodes = mobileBtn.childNodes;
      for(var i=0;i<nodes.length;i++){
        if(nodes[i].nodeType === 3){
          nodes[i].textContent = ' ' + chapterTitles[activeId];
          break;
        }
      }
    }
  }

  var ticking = false;
  window.addEventListener('scroll', function(){
    if(!ticking){
      requestAnimationFrame(function(){
        update();
        ticking = false;
      });
      ticking = true;
    }
  }, {passive:true});

  if(mobileBtn){
    mobileBtn.addEventListener('click', function(e){
      e.stopPropagation();
      document.body.classList.toggle('mobile-rail-open');
    });
  }
  document.addEventListener('click', function(e){
    if(document.body.classList.contains('mobile-rail-open')){
      if(e.target instanceof Element && !e.target.closest('.rail') && !e.target.closest('.mobile-chapter')){
        document.body.classList.remove('mobile-rail-open');
      }
    }
  });
  // Close rail when tapping a chapter link
  document.querySelectorAll('.rail a').forEach(function(a){
    a.addEventListener('click', function(){
      document.body.classList.remove('mobile-rail-open');
    });
  });

  update();
})();
