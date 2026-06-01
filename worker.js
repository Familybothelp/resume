const ALLOWED_ORIGINS = [
  'https://familybothelp.github.io',
];

const MODEL = 'openrouter/owl-alpha';
const MAX_TOKENS = 800;
const MAX_BODY_BYTES = 65536;

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

    const cl = parseInt(request.headers.get('Content-Length') || '0', 10);
    if (cl > MAX_BODY_BYTES) {
      return json({ error: 'Request too large' }, 413, corsOrigin);
    }

    try {
      const body = await request.json();
      const message = typeof body.message === 'string' ? body.message.trim() : '';
      const systemPrompt = typeof body.systemPrompt === 'string' ? body.systemPrompt.trim() : '';
      const messages = Array.isArray(body.messages) ? body.messages : [];

      if (!message && messages.length === 0) {
        return json({ error: 'message or messages required' }, 400, corsOrigin);
      }

      if (systemPrompt.length > 32000) {
        return json({ error: 'System prompt too long' }, 413, corsOrigin);
      }

      const orMessages = [{ role: 'system', content: systemPrompt }];

      if (messages.length > 0) {
        for (const m of messages) {
          if (m.role && m.content && typeof m.content === 'string') {
            if (m.content.length > 4000) continue;
            orMessages.push({ role: m.role, content: m.content });
          }
        }
      }
      if (!orMessages.some(m => m.role === 'user')) {
        orMessages.push({ role: 'user', content: message });
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

      return json({ reply: data.choices?.[0]?.message?.content || '' }, 200, corsOrigin);

    } catch (e) {
      console.error('Worker error:', e.message);
      return json({ error: 'Internal error' }, 500, corsOrigin);
    }
  },
};
