const translations = {
  fr: {
    eyebrow: 'CONTRAT TYPÉ · PLAN · EXÉCUTION · SQL',
    title: 'Quinze appels. Quatre suffisent dans cet exercice.',
    lede: 'Projetez le contexte utile, regroupez les questions communes, calculez les montants en code. Puis changez une ligne ou une politique : voyez exactement ce qui doit repartir au fournisseur.',
    experiment: 'Rejouer la comparaison',
    mode: 'État du cache et du contrat',
    cold: 'Premier passage',
    warm: 'Même entrée, deuxième passage',
    changed: 'Un seul message modifié',
    policy: 'Nouvelle version de politique',
    review: 'Confiance insuffisante',
    run: 'Exécuter les deux plans',
    fixture:
      'Fournisseur fictif déterministe pour cette démonstration. Les appels sont réellement comptés ; aucune latence ou qualité Jev n’est simulée comme une mesure.',
    cache:
      'Le cache sépare fournisseurs fictifs et réels. Sa clé inclut modèle, politique, état projeté et lot complet de questions.',
    execution: 'Appels et décisions observés',
    synthetic: 'EXÉCUTION SYNTHÉTIQUE',
    naive: 'appels du plan naïf exécuté',
    calls: 'appels du passage sélectionné',
    questions: 'questions réellement envoyées',
    dag: 'Un graphe, deux types de travail',
    arithmetic:
      'amount_due : soustraction exacte en Python. topic_copy réutilise la même question que topic. route attend topic=billing et amount_due, puis reçoit uniquement les colonnes déclarées.',
    decisions: 'Décisions par ligne',
    sql: 'Projection SQLite réellement interrogée',
    trace: 'Ce qui est parti au fournisseur',
    download: 'Exporter les plans et preuves',
    limits:
      'Alpha de choix fermés, pas un remplacement de LOTUS/Palimpzest. La réduction d’appels ne démontre ni égalité de qualité ni supériorité SOTA. Les seuils sont illustratifs. Le cache et le regroupement réutilisent des jugements ; ils ne préservent pas des échantillons stochastiques indépendants. Aucun appel payant depuis cette interface.',
    ready: 'Exécution et requête SQL terminées.',
    error: 'Plan ou entrée non valide.',
    exact: 'Calcul exact',
    choice: 'Choix typé',
    depends: 'Dépendances',
    reads: 'Colonnes',
    decided: 'Décidé',
    skipped: 'Condition non satisfaite',
    blocked_review: 'Bloqué par revue',
    reviewState: 'À revoir',
    provider_shared: 'Réponse partagée',
    provider: 'Fournisseur',
    persistent_cache: 'Cache persistant',
    provider_completed: 'Lot terminé',
    budget_exhausted: 'Budget épuisé',
    provider_error: 'Erreur fournisseur',
    context_budget: 'Contexte trop grand',
    noCalls: 'Aucune nouvelle requête : décisions relues du cache.',
  },
  en: {
    eyebrow: 'TYPED CONTRACT · PLAN · EXECUTION · SQL',
    title: 'Fifteen calls. Four suffice in this exercise.',
    lede: 'Project useful context, combine common questions and calculate amounts in code. Then change one row or policy and see exactly what must return to the provider.',
    experiment: 'Replay the comparison',
    mode: 'Cache and contract state',
    cold: 'First pass',
    warm: 'Same input, second pass',
    changed: 'One message changed',
    policy: 'New policy version',
    review: 'Insufficient confidence',
    run: 'Execute both plans',
    fixture:
      'Deterministic fixture provider for this demo. Calls are actually counted; no Jev latency or quality is simulated as a measurement.',
    cache:
      'Cache separates synthetic and real providers. Keys include model, policy, projected state and the complete question batch.',
    execution: 'Observed calls and decisions',
    synthetic: 'SYNTHETIC EXECUTION',
    naive: 'calls from executed naive plan',
    calls: 'calls in selected pass',
    questions: 'questions actually sent',
    dag: 'One graph, two kinds of work',
    arithmetic:
      'amount_due: exact Python subtraction. topic_copy reuses topic’s question. route waits for topic=billing and amount_due, then receives declared columns only.',
    decisions: 'Per-row decisions',
    sql: 'Actually queried SQLite projection',
    trace: 'What reached the provider',
    download: 'Export plans and evidence',
    limits:
      'Closed-choice alpha, not a LOTUS/Palimpzest replacement. Call reductions establish neither equal quality nor SOTA superiority. Thresholds are illustrative. Cache and batching reuse judgments; they do not preserve independent stochastic samples. No paid calls from this interface.',
    ready: 'Execution and SQL query completed.',
    error: 'Invalid plan or input.',
    exact: 'Exact computation',
    choice: 'Typed choice',
    depends: 'Dependencies',
    reads: 'Columns',
    decided: 'Decided',
    skipped: 'Condition not met',
    blocked_review: 'Blocked by review',
    reviewState: 'Needs review',
    provider_shared: 'Shared response',
    provider: 'Provider',
    persistent_cache: 'Persistent cache',
    provider_completed: 'Batch completed',
    budget_exhausted: 'Budget exhausted',
    provider_error: 'Provider error',
    context_budget: 'Context too large',
    noCalls: 'No new request: decisions loaded from cache.',
  },
  es: {
    eyebrow: 'CONTRATO TIPADO · PLAN · EJECUCIÓN · SQL',
    title: 'Quince llamadas. Cuatro bastan en este ejercicio.',
    lede: 'Proyecte contexto útil, agrupe preguntas comunes y calcule importes en código. Cambie una fila o política y vea qué debe volver al proveedor.',
    experiment: 'Repetir la comparación',
    mode: 'Estado de caché y contrato',
    cold: 'Primera pasada',
    warm: 'Misma entrada, segunda pasada',
    changed: 'Un mensaje modificado',
    policy: 'Nueva versión de política',
    review: 'Confianza insuficiente',
    run: 'Ejecutar ambos planes',
    fixture:
      'Proveedor ficticio determinista. Las llamadas se cuentan realmente; no se simula latencia ni calidad Jev como medida.',
    cache:
      'La caché separa proveedores ficticios y reales. La clave incluye modelo, política, estado proyectado y lote completo de preguntas.',
    execution: 'Llamadas y decisiones observadas',
    synthetic: 'EJECUCIÓN SINTÉTICA',
    naive: 'llamadas del plan ingenuo ejecutado',
    calls: 'llamadas de la pasada elegida',
    questions: 'preguntas realmente enviadas',
    dag: 'Un grafo, dos tipos de trabajo',
    arithmetic:
      'amount_due: resta exacta en Python. topic_copy reutiliza la pregunta topic. route espera topic=billing y amount_due y recibe solo columnas declaradas.',
    decisions: 'Decisiones por fila',
    sql: 'Proyección SQLite consultada realmente',
    trace: 'Lo que recibió el proveedor',
    download: 'Exportar planes y pruebas',
    limits:
      'Alfa de elecciones cerradas, no sustituto de LOTUS/Palimpzest. Menos llamadas no demuestra igual calidad ni superioridad SOTA. Umbrales ilustrativos. Caché y agrupación reutilizan juicios; no conservan muestras estocásticas independientes. Sin llamadas de pago desde esta interfaz.',
    ready: 'Ejecución y consulta SQL terminadas.',
    error: 'Plan o entrada no válido.',
    exact: 'Cálculo exacto',
    choice: 'Elección tipada',
    depends: 'Dependencias',
    reads: 'Columnas',
    decided: 'Decidido',
    skipped: 'Condición no satisfecha',
    blocked_review: 'Bloqueado por revisión',
    reviewState: 'Revisar',
    provider_shared: 'Respuesta compartida',
    provider: 'Proveedor',
    persistent_cache: 'Caché persistente',
    provider_completed: 'Lote terminado',
    budget_exhausted: 'Presupuesto agotado',
    provider_error: 'Error del proveedor',
    context_budget: 'Contexto demasiado grande',
    noCalls: 'Sin peticiones nuevas: decisiones leídas de caché.',
  },
};
const lang = new URLSearchParams(location.search).get('lang') || 'en',
  t = translations[lang] || translations.en;
document.documentElement.lang = translations[lang] ? lang : 'en';
document.querySelectorAll('[data-i18n]').forEach((e) => (e.textContent = t[e.dataset.i18n]));
const $ = (id) => document.getElementById(id);
let evidence;
function el(tag, text, cls) {
  const n = document.createElement(tag);
  n.textContent = text;
  if (cls) n.className = cls;
  return n;
}
async function run() {
  try {
    $('run').disabled = true;
    const response = await fetch('/api/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lang: document.documentElement.lang, mode: $('mode').value }),
    });
    if (!response.ok) throw Error();
    evidence = await response.json();
    const r = evidence.selected;
    $('naive').textContent = evidence.baseline.provider_calls;
    $('calls').textContent = r.provider_calls;
    $('questions').textContent = r.questions_sent;
    $('digest').textContent = r.plan_sha256;
    $('dag').replaceChildren();
    for (const node of Object.values(evidence.compiled.nodes)) {
      const div = el('div', '', `node ${node.kind === 'subtract' ? 'exact' : ''}`);
      div.append(
        el('strong', node.id),
        el('p', node.kind === 'subtract' ? t.exact : t.choice),
        el('code', `${t.reads}: ${node.reads.join(', ')}`),
        el('code', `${t.depends}: ${node.depends.join(', ') || '—'}`),
      );
      $('dag').append(div);
    }
    $('rows').replaceChildren();
    for (const [id, nodes] of Object.entries(r.rows)) {
      const card = el('section', '', 'row-card');
      card.append(el('h3', id));
      const cells = el('div', '', 'cells');
      for (const [node, value] of Object.entries(nodes)) {
        const cell = el('div', '', `cell ${value.status}`);
        cell.append(
          el('strong', node),
          el(
            'p',
            value.choice ??
              (value.value !== undefined ? String(value.value) : (t[value.status] ?? value.status)),
          ),
          el(
            'small',
            value.status === 'review' ? t.reviewState : (t[value.status] ?? value.status),
          ),
        );
        if (value.origin) cell.append(el('p', t[value.origin], 'hint'));
        cells.append(cell);
      }
      card.append(cells);
      $('rows').append(card);
    }
    $('sql').textContent = evidence.sql;
    $('sql-rows').textContent = JSON.stringify(evidence.sql_rows, null, 2);
    $('trace').replaceChildren();
    if (!r.trace.length) $('trace').append(el('p', t.noCalls));
    for (const step of r.trace) {
      const div = el('details', '', 'trace');
      div.append(
        el(
          'summary',
          `${t[step.status] ?? step.status} · ${step.question_count ?? step.questions}`,
        ),
        el('pre', JSON.stringify(step, null, 2)),
      );
      $('trace').append(div);
    }
    $('status').textContent = t.ready;
  } catch {
    $('status').textContent = t.error;
  } finally {
    $('run').disabled = false;
  }
}
$('run').onclick = run;
$('download').onclick = () => {
  if (!evidence) return;
  const url = URL.createObjectURL(
      new Blob([JSON.stringify(evidence, null, 2)], { type: 'application/json' }),
    ),
    a = document.createElement('a');
  a.href = url;
  a.download = 'semantic-plan-evidence.json';
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};
await run();
