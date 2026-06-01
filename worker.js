const ALLOWED_ORIGINS = [
  'https://familybothelp.github.io',
];

const MODEL = 'openrouter/owl-alpha';
const MAX_TOKENS = 800;
const MAX_BODY_BYTES = 65536;
const MAX_QUESTIONS = 20;
const MAX_QUESTION_LENGTH = 1500;
const ALLOWED_ROLES = new Set(['user', 'assistant']);

const SYSTEM_PROMPT = `Ты — AI-агент интерактивного резюме. Твоя задача — отвечать на вопросы о кандидате Евгении Мешкове, помогать работодателям понять, подходит ли он их компании, и давать живое представление о нём как о специалисте и человеке.

ДАННЫЕ ЕВГЕНИЯ:
- Полное имя: Мешков Евгений Александрович
- Псевдоним: Арон Родович
- Дата рождения: 01.03.1993 (33 года)
- Семейное положение: женат, есть ребёнок
- Английский: B2 (чтение технической документации, переписка)
- Город: Московская область, г.о. Чехов
- Любимый цвет: бутылочно-зелёный
- Любимая еда: картошка фри и стейк
- Хобби: технологии, AI, проза (пишет книги под псевдонимом), эксперименты с LLM
- Самоучка: не имеет профильного IT-образования, всему научился сам
- Тип мышления: практик и инженер — сначала работает прототип, потом теория
- Принцип работы: проектирует систему → AI пишет код → он отлаживает и улучшает
- Опыт работы: менеджер по продажам, оператор по поиску и переправке грузов в США
- Образование: среднее профессиональное (колледж)

ПОЗИЦИОНИРОВАНИЕ:
Должность: AI Workflow Designer / Специалист по внедрению AI
Зарплата: от 150 000 ₽
Формат: удалённо
График: гибкий, полный день

ЧТО ДЕЛАЛ НА ПРАКТИКЕ:
- Мультиагентные системы: архитектура ролей, оркестрация, @mention-пайплайн, agent tool loop (5 раундов, 8 вызовов)
- Управление контекстом LLM: скользящее окно, суммаризация, 4-слойное хранение (rules/journal/canon/experience)
- RAG: ChromaDB, эмбеддинги (all-MiniLM), hybrid retrieval
- Tool calling: structured output, multi-round loop
- Сравнительное тестирование LLM
- Локальные модели: GGUF/MLX, kv-cache quantization
- API-модели: OpenRouter, multi-key ротация
- Prompt engineering: system prompts, few-shot, role-based
- AI-инфраструктура: macOS + Windows Server, прокси, gateway

СТИЛЬ ОТВЕТОВ:
- Отвечай тепло, но профессионально. Как будто ты — личный ассистент Евгения.
- Если вопрос не по теме резюме (погода, политика, развлечения) — мягко возвращай к теме.
- Если не знаешь ответа — честно признайся и предложи пригласить Евгения на собеседование.
- Не придумывай факты о Евгении. Используй только данные выше.
- Отвечай кратко (2-5 предложений), если не попросили развёрнуто.
- Спрашивай уточняющие вопросы, если нужно понять контекст работодателя.
- Если вопрос предполагает сравнение — объясни, что Евгений изучает AI с середины 2025 года и быстро учится.`.trim();

// Простейший rate limiter in-memory (сбрасывается при перезагрузке worker)
const rateLimit = new Map();
const RATE_WINDOW_MS = 60000;
const RATE_MAX_REQUESTS = 30;

function checkRateLimit(ip) {
  const now = Date.now();
  const entry = rateLimit.get(ip);
  if (!entry || now - entry.windowStart > RATE_WINDOW_MS) {
    rateLimit.set(ip, { windowStart: now, count: 1 });
    return true;
  }
  if (entry.count >= RATE_MAX_REQUESTS) return false;
  entry.count++;
  return true;
}

function json(data, status = 200, corsOrigin = '*') {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Access-Control-Allow-Origin': corsOrigin, 'Content-Type': 'application/json' },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const corsOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : 'https://familybothelp.github.io';
    const corsHeaders = { 'Access-Control-Allow-Origin': corsOrigin };

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: { ...corsHeaders, 'Access-Control-Allow-Methods': 'POST, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400' },
      });
    }

    if (request.method !== 'POST') {
      return json({ error: 'Method not allowed' }, 405, corsOrigin);
    }

    const apiKey = env.OPENROUTER_KEY;
    if (!apiKey) {
      return json({ error: 'Service not configured' }, 500, corsOrigin);
    }

    // Rate limiting
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (!checkRateLimit(ip)) {
      return json({ error: 'Too many requests. Try again later.' }, 429, corsOrigin);
    }

    const cl = parseInt(request.headers.get('Content-Length') || '0', 10);
    if (cl > MAX_BODY_BYTES) {
      return json({ error: 'Request too large' }, 413, corsOrigin);
    }

    try {
      const body = await request.json();
      if (!body || typeof body !== 'object') {
        return json({ error: 'Invalid request body' }, 400, corsOrigin);
      }

      const message = typeof body.message === 'string' ? body.message.trim() : '';
      const messages = Array.isArray(body.messages) ? body.messages : [];

      if (!message && messages.length === 0) {
        return json({ error: 'message or messages required' }, 400, corsOrigin);
      }

      if (message.length > MAX_QUESTION_LENGTH) {
        return json({ error: `Question too long (max ${MAX_QUESTION_LENGTH} chars)` }, 413, corsOrigin);
      }

      const orMessages = [{ role: 'system', content: SYSTEM_PROMPT }];

      let msgCount = 0;
      if (messages.length > 0) {
        for (const m of messages) {
          if (!ALLOWED_ROLES.has(m.role)) continue;
          if (typeof m.content !== 'string' || !m.content.trim()) continue;
          if (m.content.length > MAX_QUESTION_LENGTH) continue;
          orMessages.push({ role: m.role, content: m.content.trim() });
          if (m.role === 'user') msgCount++;
        }
      }

      if (!orMessages.some(m => m.role === 'user')) {
        orMessages.push({ role: 'user', content: message });
        msgCount++;
      }

      if (msgCount > MAX_QUESTIONS) {
        return json({ error: 'Dialog limit reached (max 20 questions)' }, 413, corsOrigin);
      }

      const orResponse = await fetch('https://openrouter.ai/api/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`,
          'HTTP-Referer': 'https://familybothelp.github.io/resume/',
          'X-Title': 'Interactive Resume AI Agent',
        },
        body: JSON.stringify({
          model: MODEL,
          messages: orMessages,
          temperature: 0.7,
          max_tokens: MAX_TOKENS,
        }),
      });

      const data = await orResponse.json();

      if (!orResponse.ok) {
        console.error('OpenRouter error:', data.error?.message || 'Unknown');
        return json({ error: 'AI service error' }, 502, corsOrigin);
      }

      // Логируем успешный запрос (простой счётчик в env, если нужно)
      if (env.REQUEST_LOG) {
        await env.REQUEST_LOG.put(
          `${ip}-${Date.now()}`,
          JSON.stringify({ ip, time: Date.now(), msgCount })
        );
      }

      return json({ reply: data.choices?.[0]?.message?.content || '' }, 200, corsOrigin);

    } catch (e) {
      console.error('Worker error:', e.message);
      return json({ error: 'Internal error' }, 500, corsOrigin);
    }
  },
};
