const STORAGE_KEY = "three-day-learning-v1";

const days = [
  {
    id: "tonight",
    label: "今晚 · 06.19",
    title: "先把判断变成可检查的东西",
    note: "今晚不要贪多。只处理决策、价格、宏观、流程、注意力和逻辑，目标是把脑子里的判断落到纸面。",
    items: [
      ["01", "经济学的思维方式", "把投资、职业、健康、关系放进同一张稀缺资源表", "复盘一个最近选择：显性收益、隐性成本、放弃选项"],
      ["02", "经济学原理", "把价格、政策、激励和市场预期连起来", "选一个持仓，写价格隐含了什么预期"],
      ["03", "经济学", "把宏观新闻翻译成利率、汇率、通胀、信用、风险偏好", "用最近一条宏观新闻测试组合脆弱点"],
      ["04", "管理学", "把个人能力变成流程和作品", "为第二曲线写目标、资源、流程、反馈、纠偏"],
      ["06", "逻辑学导论", "给所有强观点加前提、反例和失效信号", "拆一条你最相信的投资判断"],
      ["09", "心理学导论", "把注意力、压力、学习和情绪当成可维护系统", "写坏状态下不做不可逆决定的触发清单"]
    ]
  },
  {
    id: "tomorrow",
    label: "明天 · 06.20",
    title: "用小实验检查市场、组织和自己",
    note: "明天的重点是验证，不是理解更多概念。每个动作都要产出一张表、一个问题或一个小实验。",
    items: [
      ["05", "组织行为学", "把大厂经验沉淀为组织诊断能力", "画一个客户或组织的真实影响力地图"],
      ["10", "社会心理学", "防止群体共识和身份压力污染判断", "给一个热门市场观点写反方证据"],
      ["11", "进化心理学", "拆开安全感、地位、资源、亲密关系的底层驱动", "把一个资产目标拆成理性、情绪、比较三层"],
      ["12", "实验心理学", "把计划变成可验证小实验", "给健康或第二曲线设计一个只改一个变量的实验"],
      ["13", "行为科学统计", "用基准率、分布、均值回归保护判断", "对一个高预期资产写最坏 10% 情景"],
      ["15", "社会研究方法", "用访谈和观察验证真实需求", "设计 3 个只问过去行为的客户访谈问题"]
    ]
  },
  {
    id: "after",
    label: "后天 · 06.21",
    title: "把边界、制度和表达固化下来",
    note: "后天只做收束：哪些要规则化，哪些要拒绝，哪些要说清楚。学习结果必须进入生活系统。",
    items: [
      ["07", "法律之门", "把资产、关系、承诺和证据放进可执行边界", "列出伴侣、家庭、跨境账户需要规则化的事项"],
      ["08", "大问题：简明哲学导论", "防止资产目标吞掉好生活目标", "把关键海外资产目标翻译成 3 个拒绝权"],
      ["14", "社会学", "看见平台、阶层、城市、网络和作品这些结构资本", "复盘结构资本：平台、资产、网络、城市、作品"],
      ["16", "人类学", "把未来生活从抽象目标变成仪式和空间", "设计一个每周稳定生活、伴侣或学习仪式"],
      ["17", "国家的常识", "把市场放进制度、财政、政策和规则稳定性里", "给一个跨境资产写制度暴露表"],
      ["18", "沟通的艺术", "把判断变成别人能接收、能行动的表达", "重要沟通前写：对方想要、害怕、我能提供、边界"]
    ]
  }
];

const board = document.querySelector("#board");
const dayTemplate = document.querySelector("#dayTemplate");
const cardTemplate = document.querySelector("#cardTemplate");
const timelineButtons = [...document.querySelectorAll(".timeline-item")];
const progressText = document.querySelector("#progressText");
const progressPercent = document.querySelector("#progressPercent");
const ringFill = document.querySelector("#ringFill");
const resetButton = document.querySelector("#resetButton");

const loadState = () => {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
  } catch {
    return {};
  }
};

const saveState = (state) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
};

let state = loadState();

function render() {
  board.innerHTML = "";

  days.forEach((day) => {
    const section = dayTemplate.content.firstElementChild.cloneNode(true);
    section.dataset.day = day.id;
    section.classList.toggle("visible", day.id === "tonight");
    section.querySelector(".day-label").textContent = day.label;
    section.querySelector("h2").textContent = day.title;
    section.querySelector(".day-heading p").textContent = day.note;

    const cards = section.querySelector(".cards");
    day.items.forEach(([no, title, value, action]) => {
      const key = `${day.id}-${no}`;
      const card = cardTemplate.content.firstElementChild.cloneNode(true);
      const checkbox = card.querySelector("input");
      const textarea = card.querySelector("textarea");

      checkbox.checked = Boolean(state[key]?.done);
      textarea.value = state[key]?.note || "";
      card.classList.toggle("done", checkbox.checked);
      card.querySelector(".book-no").textContent = `${no} |`;
      card.querySelector("h3").textContent = title;
      card.querySelector(".value-line").textContent = value;
      card.querySelector(".action-box strong").textContent = action;

      checkbox.addEventListener("change", () => {
        state[key] = { ...(state[key] || {}), done: checkbox.checked, note: textarea.value };
        card.classList.toggle("done", checkbox.checked);
        saveState(state);
        updateProgress();
      });

      textarea.addEventListener("input", () => {
        state[key] = { ...(state[key] || {}), done: checkbox.checked, note: textarea.value };
        saveState(state);
      });

      cards.appendChild(card);
    });

    board.appendChild(section);
  });

  updateProgress();
}

function showDay(dayId) {
  document.querySelectorAll(".day-section").forEach((section) => {
    section.classList.toggle("visible", section.dataset.day === dayId);
  });
  timelineButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.day === dayId);
  });
}

function updateProgress() {
  const total = days.reduce((sum, day) => sum + day.items.length, 0);
  const done = days.reduce((sum, day) => {
    return sum + day.items.filter(([no]) => state[`${day.id}-${no}`]?.done).length;
  }, 0);
  const percent = Math.round((done / total) * 100);
  const circumference = 2 * Math.PI * 48;
  ringFill.style.strokeDashoffset = `${circumference - (percent / 100) * circumference}`;
  progressText.textContent = `${done}/${total}`;
  progressPercent.textContent = `${percent}%`;
}

timelineButtons.forEach((button) => {
  button.addEventListener("click", () => showDay(button.dataset.day));
});

resetButton.addEventListener("click", () => {
  state = {};
  saveState(state);
  render();
});

render();
