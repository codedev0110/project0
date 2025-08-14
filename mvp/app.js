// Simple SPA router and state
const state = {
	view: 'dashboard',
	user: null,
	projects: [],
	commentsByProject: {},
	ratingsByProject: {},
	openaiKey: localStorage.getItem('openai_key') || '',
};

// Seed demo data
const demoProjects = [
	{
		id: 'p1',
		title: 'Python: Fibonacci',
		description: 'Sadə Fibonacci funksiyası.',
		language: 'PYTHON',
		skillLevel: 'BEGINNER',
		technologies: ['Python'],
		version: '1.0.0',
		codeMarkdown: '```python\ndef fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return a\n\nprint(fib(10))\n```',
	},
	{
		id: 'p2',
		title: 'JavaScript: Array Utils',
		description: 'Filter və map nümunəsi.',
		language: 'JAVASCRIPT',
		skillLevel: 'INTERMEDIATE',
		technologies: ['JavaScript'],
		version: '1.1.0',
		codeMarkdown: '```javascript\nconst nums = [1,2,3,4,5];\nconst evenSquares = nums.filter(n => n % 2 === 0).map(n => n*n);\nconsole.log(evenSquares);\n```',
	},
];

function loadState() {
	const savedUser = localStorage.getItem('mvp_user');
	if (savedUser) state.user = JSON.parse(savedUser);
	state.projects = JSON.parse(localStorage.getItem('mvp_projects') || 'null') || demoProjects;
	state.commentsByProject = JSON.parse(localStorage.getItem('mvp_comments') || '{}');
	state.ratingsByProject = JSON.parse(localStorage.getItem('mvp_ratings') || '{}');
}

function saveState() {
	localStorage.setItem('mvp_projects', JSON.stringify(state.projects));
	localStorage.setItem('mvp_comments', JSON.stringify(state.commentsByProject));
	localStorage.setItem('mvp_ratings', JSON.stringify(state.ratingsByProject));
	if (state.user) localStorage.setItem('mvp_user', JSON.stringify(state.user));
}

// Auth UI
function renderAuthArea() {
	const container = document.getElementById('authArea');
	container.innerHTML = '';
	if (state.user) {
		const span = document.createElement('span');
		span.className = 'text-sm text-slate-600';
		span.textContent = `Salam, ${state.user.name}`;
		const btn = document.createElement('button');
		btn.className = 'ml-2 px-3 py-1.5 rounded border hover:bg-slate-100';
		btn.textContent = 'Çıxış';
		btn.onclick = () => { state.user = null; localStorage.removeItem('mvp_user'); render(); };
		container.appendChild(span);
		container.appendChild(btn);
	} else {
		const loginBtn = document.createElement('button');
		loginBtn.className = 'px-3 py-1.5 rounded bg-indigo-600 text-white';
		loginBtn.textContent = 'Daxil ol';
		loginBtn.onclick = openLoginModal;
		const signupBtn = document.createElement('button');
		signupBtn.className = 'px-3 py-1.5 rounded border';
		signupBtn.textContent = 'Qeydiyyat';
		signupBtn.onclick = openSignupModal;
		container.appendChild(loginBtn);
		container.appendChild(signupBtn);
	}
}

function openLoginModal() {
	renderAuthModal('login');
}
function openSignupModal() {
	renderAuthModal('signup');
}

function renderAuthModal(mode) {
	const root = document.getElementById('authModals');
	root.innerHTML = '';
	const overlay = document.createElement('div');
	overlay.className = 'fixed inset-0 bg-black/40 flex items-center justify-center z-50';
	const card = document.createElement('div');
	card.className = 'bg-white rounded border w-full max-w-sm p-4';
	card.innerHTML = `
		<h3 class="font-semibold mb-3">${mode === 'login' ? 'Daxil ol' : 'Qeydiyyat'}</h3>
		<div class="space-y-2">
			<input id="authName" class="border rounded px-3 py-2 w-full" placeholder="Ad" ${mode==='login'?'style="display:none"':''} />
			<input id="authEmail" class="border rounded px-3 py-2 w-full" placeholder="Email" />
			<input id="authPass" type="password" class="border rounded px-3 py-2 w-full" placeholder="Şifrə" />
			<div class="flex items-center justify-end gap-2">
				<button id="cancelAuth" class="px-3 py-1.5 rounded border">Bağla</button>
				<button id="confirmAuth" class="px-3 py-1.5 rounded bg-indigo-600 text-white">Təsdiqlə</button>
			</div>
		</div>
	`;
	overlay.appendChild(card);
	root.appendChild(overlay);
	document.getElementById('cancelAuth').onclick = () => { root.innerHTML = ''; };
	document.getElementById('confirmAuth').onclick = () => {
		const email = document.getElementById('authEmail').value.trim();
		const pass = document.getElementById('authPass').value.trim();
		if (!email || !pass) return;
		if (mode === 'signup') {
			const name = document.getElementById('authName').value.trim() || email.split('@')[0];
			state.user = { id: 'u_'+Date.now(), email, name };
		} else {
			state.user = { id: 'u_demo', email, name: email.split('@')[0] };
		}
		saveState();
		root.innerHTML = '';
		render();
	};
}

// Dashboard rendering
function renderDashboard() {
	document.getElementById('dashboardView').classList.remove('hidden');
	document.getElementById('projectView').classList.add('hidden');
	document.getElementById('settingsView').classList.add('hidden');

	const list = document.getElementById('projectList');
	list.innerHTML = '';
	const language = document.getElementById('languageFilter').value;
	const level = document.getElementById('levelFilter').value;
	const sort = document.getElementById('sortFilter').value;
	const q = document.getElementById('searchInput').value.toLowerCase();

	let items = [...state.projects];
	if (language) items = items.filter(p => p.language === language);
	if (level) items = items.filter(p => p.skillLevel === level);
	if (q) items = items.filter(p => (p.title + ' ' + p.description).toLowerCase().includes(q));
	if (sort === 'new') items.sort((a,b) => (a.id < b.id ? 1 : -1));
	if (sort === 'popular') items.sort((a,b) => avgRating(b.id) - avgRating(a.id));

	for (const p of items) {
		const card = document.createElement('div');
		card.className = 'border rounded p-4 bg-white hover:shadow transition cursor-pointer';
		card.innerHTML = `
			<div class="flex items-start justify-between">
				<div>
					<h3 class="font-semibold">${p.title}</h3>
					<p class="text-sm text-slate-600">${p.description}</p>
				</div>
				<div class="text-sm text-slate-500">${avgRating(p.id).toFixed(1)} ⭐</div>
			</div>
			<div class="mt-2 text-xs text-slate-500">Dil: ${p.language} • Səviyyə: ${p.skillLevel}</div>
		`;
		card.onclick = () => openProject(p.id);
		list.appendChild(card);
	}
}

function avgRating(projectId) {
	const arr = state.ratingsByProject[projectId] || [];
	if (!arr.length) return 0;
	return arr.reduce((s, r) => s + r.value, 0) / arr.length;
}

// Project page rendering
function openProject(projectId) {
	history.replaceState({}, '', `#/project/${projectId}`);
	renderProject(projectId);
}

function renderProject(projectId) {
	document.getElementById('dashboardView').classList.add('hidden');
	document.getElementById('projectView').classList.remove('hidden');
	document.getElementById('settingsView').classList.add('hidden');

	const project = state.projects.find(p => p.id === projectId);
	if (!project) return;
	document.getElementById('projectTitle').textContent = project.title;
	document.getElementById('projectDescription').textContent = project.description;
	document.getElementById('projectLanguage').textContent = project.language;
	document.getElementById('projectLevel').textContent = project.skillLevel;
	document.getElementById('projectTech').textContent = project.technologies.join(', ');
	document.getElementById('projectVersion').textContent = project.version;
	document.getElementById('projectAvgRating').textContent = `${avgRating(project.id).toFixed(1)} / 5`;

	renderCode(project);
	renderComments(project);
	renderRating(project);
}

function renderCode(project) {
	const container = document.getElementById('codeContainer');
	container.innerHTML = '';

	// Render markdown with code fences
	const html = marked.parse(project.codeMarkdown);
	const wrapper = document.createElement('div');
	wrapper.innerHTML = html;

	// Enhance code blocks
	wrapper.querySelectorAll('pre code').forEach((codeEl) => {
		const pre = codeEl.parentElement;
		pre.classList.add('code-block');
		const blockText = codeEl.textContent;
		const btn = document.createElement('button');
		btn.className = 'explain-btn';
		btn.textContent = '?';
		btn.onclick = (e) => {
			e.stopPropagation();
			openExplainPopover(pre, project, blockText);
		};
		pre.appendChild(btn);
	});

	container.appendChild(wrapper);
	Prism.highlightAllUnder(container);
}

function openExplainPopover(anchorEl, project, code) {
	closeAllPopovers();
	const pop = document.createElement('div');
	pop.className = 'popover';
	pop.innerHTML = `
		<button class="close text-slate-400">✕</button>
		<h4>Kod izahı</h4>
		<div class="text-sm" id="explainText">Yüklənir...</div>
		<div class="mt-2 flex items-center gap-2">
			<input id="askInput" class="border rounded px-2 py-1 w-full" placeholder="Sual ver (opsional)" />
			<button id="askBtn" class="px-2 py-1 rounded border">Sor</button>
		</div>
	`;
	anchorEl.appendChild(pop);
	pop.querySelector('.close').onclick = closeAllPopovers;

	explainCode({ code, language: project.language }).then(text => {
		pop.querySelector('#explainText').textContent = text;
	});
	pop.querySelector('#askBtn').onclick = async () => {
		const q = pop.querySelector('#askInput').value.trim();
		if (!q) return;
		pop.querySelector('#explainText').textContent = 'Yüklənir...';
		const txt = await explainCode({ code, language: project.language, question: q });
		pop.querySelector('#explainText').textContent = txt;
	};
}

function closeAllPopovers() {
	document.querySelectorAll('.popover').forEach(el => el.remove());
}

async function explainCode({ code, language, question }) {
	if (!state.openaiKey) {
		return localExplain({ code, language, question });
	}
	try {
		const body = {
			model: 'gpt-4o-mini',
			messages: [
				{ role: 'system', content: `Sən ${language} üzrə təcrübəli mentorus.` },
				{ role: 'user', content: `${question ? 'Sual: ' + question + '\n\n' : ''}Kod:\n${code}` }
			],
			temperature: 0.2
		};
		const res = await fetch('https://api.openai.com/v1/chat/completions', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${state.openaiKey}`,
			},
			body: JSON.stringify(body)
		});
		if (!res.ok) throw new Error('AI sorğusu uğursuz oldu');
		const data = await res.json();
		return data.choices?.[0]?.message?.content || 'İzah tapılmadı.';
	} catch (e) {
		return `Xəta: ${e.message}`;
	}
}

function localExplain({ code, language, question }) {
	const hints = [];
	if (language === 'PYTHON' && code.includes('for')) hints.push('Dövr sayğacı ilə ardıcıllıq üzərində iterasiya edilir.');
	if (language === 'JAVASCRIPT' && code.includes('map')) hints.push('Array.map hər elementi transformasiya edir.');
	if (code.includes('return')) hints.push('Funksiya nəticəni return ilə qaytarır.');
	if (!hints.length) hints.push('Kodun məqsədi və axını sadə şəkildə göstərilmişdir.');
	if (question) hints.push(`Suala cavab: ${question}`);
	return hints.join(' ');
}

// Comments
function renderComments(project) {
	const wrapper = document.getElementById('commentsList');
	wrapper.innerHTML = '';
	const list = state.commentsByProject[project.id] || [];
	for (const c of list) {
		const div = document.createElement('div');
		div.className = 'border rounded p-2';
		div.innerHTML = `<div class="text-sm font-medium">${c.author}</div><div class="text-sm text-slate-700">${c.text}</div>`;
		wrapper.appendChild(div);
	}

	const formArea = document.getElementById('commentFormArea');
	formArea.innerHTML = '';
	if (!state.user) {
		formArea.innerHTML = '<div class="text-sm text-slate-600">Rəy yazmaq üçün daxil olun.</div>';
		return;
	}
	const ta = document.createElement('textarea');
	ta.className = 'border rounded px-3 py-2 w-full';
	ta.placeholder = 'Rəyinizi yazın...';
	const btn = document.createElement('button');
	btn.className = 'mt-2 px-3 py-1.5 rounded bg-indigo-600 text-white';
	btn.textContent = 'Göndər';
	btn.onclick = () => {
		const text = ta.value.trim();
		if (!text) return;
		state.commentsByProject[project.id] = [...(state.commentsByProject[project.id]||[]), { id: 'c_'+Date.now(), author: state.user.name, text }];
		saveState();
		renderComments(project);
	};
	formArea.appendChild(ta);
	formArea.appendChild(btn);
}

// Ratings
function renderRating(project) {
	const input = document.getElementById('ratingInput');
	const btn = document.getElementById('rateBtn');
	btn.onclick = () => {
		const value = Number(input.value);
		if (!value || value < 1 || value > 5) return;
		if (!state.user) { alert('Qiymət vermək üçün daxil olun.'); return; }
		const arr = state.ratingsByProject[project.id] || [];
		const existingIdx = arr.findIndex(r => r.userId === state.user.id);
		if (existingIdx >= 0) arr[existingIdx].value = value; else arr.push({ userId: state.user.id, value });
		state.ratingsByProject[project.id] = arr;
		saveState();
		document.getElementById('projectAvgRating').textContent = `${avgRating(project.id).toFixed(1)} / 5`;
	};
}

// Settings
function renderSettings() {
	document.getElementById('dashboardView').classList.add('hidden');
	document.getElementById('projectView').classList.add('hidden');
	document.getElementById('settingsView').classList.remove('hidden');
	const input = document.getElementById('openaiKeyInput');
	input.value = state.openaiKey || '';
	document.getElementById('saveKeyBtn').onclick = () => {
		state.openaiKey = input.value.trim();
		if (state.openaiKey) localStorage.setItem('openai_key', state.openaiKey);
		alert('Yadda saxlandı');
	};
	document.getElementById('clearKeyBtn').onclick = () => {
		state.openaiKey = '';
		localStorage.removeItem('openai_key');
		input.value = '';
	};
}

// Router
function handleRoute() {
	const hash = location.hash || '#/dashboard';
	if (hash.startsWith('#/project/')) {
		const id = hash.split('/')[2];
		renderProject(id);
		return;
	}
	if (hash.startsWith('#/settings')) {
		renderSettings();
		return;
	}
	renderDashboard();
}

function attachEvents() {
	document.getElementById('dashboardLink').onclick = () => { history.replaceState({}, '', '#/dashboard'); renderDashboard(); };
	document.getElementById('settingsLink').onclick = () => { history.replaceState({}, '', '#/settings'); renderSettings(); };
	document.getElementById('backToDashboard').onclick = () => { history.replaceState({}, '', '#/dashboard'); renderDashboard(); };
	['languageFilter','levelFilter','sortFilter','searchInput'].forEach(id => {
		const el = document.getElementById(id);
		el.onchange = renderDashboard;
		el.oninput = renderDashboard;
	});
	window.addEventListener('hashchange', handleRoute);
}

function render() {
	renderAuthArea();
	handleRoute();
}

// Init
loadState();
attachEvents();
render();