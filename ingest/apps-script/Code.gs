const OWNER = 'Carlping';
const REPO = 'awesome-recruiter';

function first_(namedValues, title) {
  const values = namedValues[title] || [''];
  return values[0];
}

function onFormSubmit(e) {
  const v = e.namedValues;
  const review = {
    recruiter: {
      name: first_(v, 'Recruiter 顯示名稱'),
      type: first_(v, 'Recruiter 類型'),
      company: first_(v, 'Recruiter 所屬公司'),
      linkedin: first_(v, 'Recruiter LinkedIn') || null
    },
    hiring_company: first_(v, '應徵公司') || null,
    industry: first_(v, '產業'),
    country: first_(v, '國家／地區'),
    admin_area: first_(v, '州／省（選填）') || null,
    metro: first_(v, '城市／都會區（選填）') || null,
    role_family: first_(v, '職務族群'),
    seniority: first_(v, '職級'),
    channel: first_(v, '接觸管道'),
    period: first_(v, '評價月份'),
    stage_reached: first_(v, '走到的階段'),
    score_responsiveness: first_(v, '回應速度'),
    score_transparency: first_(v, '資訊透明'),
    score_professionalism: first_(v, '專業度'),
    score_respect: first_(v, '尊重'),
    score_closure: first_(v, '結果通知'),
    ghosted: first_(v, '是否無聲卡'),
    salary_disclosed_upfront: first_(v, '是否事前揭露薪資'),
    would_engage_again: first_(v, '是否願意再次接觸'),
    summary: first_(v, '經驗摘要')
  };
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  const url = `https://api.github.com/repos/${OWNER}/${REPO}/dispatches`;
  UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json' },
    payload: JSON.stringify({ event_type: 'new_review', client_payload: { review: review } }),
    muteHttpExceptions: false
  });
}

function setup() {
  const form = FormApp.getActiveForm();
  ScriptApp.newTrigger('onFormSubmit').forForm(form).onFormSubmit().create();
}
