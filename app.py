from functools import reduce
from flask import Flask, request

from kefir.predication import Person
from kefir.subject import (
  nominative,
  ablative,
  accusative,
  genitive,
  possesive,
  dative,
  locative
)

from kefir.predication import (
  zero,
  tobe,
  personal,
  inferential,
  conditional,
  perfective,
  imperfective,
  future,
  progressive,
  necessitative,
  impotential,
  first_person_singular,
  second_person_singular,
  third_person_singular,
  first_person_plural,
  second_person_plural,
  third_person_plural,
)

app = Flask(__name__)

CASES = [
  nominative,
  ablative,
  accusative,
  genitive,
  possesive,
  dative,
  locative,
]

COPULAS = [
  zero,
  tobe,
  personal,
  inferential,
  conditional,
  perfective,
  imperfective,
  future,
  progressive,
  necessitative,
  impotential,
]

COLOR_MAP = {
  nominative: 'DeepPink',
  ablative: 'Violet',
  accusative: 'Crimson',
  genitive: 'MediumPurple',
  possesive: 'BlueViolet',
  dative: 'LightSkyBlue',
  locative: 'DodgerBlue',
  zero: 'Blue',
  tobe: 'Salmon',
  personal: 'Tomato',
  inferential: 'HotPink',
  conditional: 'LightGreen',
  perfective: 'MediumSlateBlue',
  imperfective: 'MediumTurquoise',
  future: 'Aquamarine',
  progressive: 'Coral',
  necessitative: 'ForestGreen',
  impotential: 'Gold',
}

WHOM = [
  first_person_singular,
  second_person_singular,
  third_person_singular,
  first_person_plural,
  second_person_plural,
  third_person_plural,
]

BREAK_LINE = '<br />'
NOTHING = ''

BASE_TEMPLATE = '''
  <!DOCTYPE html>
  <html lang="en">
    <head>
      <title>Kefir</title>
      <link href="static/style.css" rel="stylesheet" />
    </head>
    <body>
    <img
      width="200"
      src="static/kefir.svg"
    />
    %(content)s
    </body>
  </html>
'''

CASE_TEMPLATE = '''
  <p class="radio-line">
    <input %(checked)s type="radio" name="case" id="%(value)s" value="%(value)s">
    <label for="%(value)s">%(name)s</label>
    <code>%(docs)s</code>
  </p>
'''

COPULA_TEMPLATE = '''
  <p class="checkbox-line">
    <input %(checked)s type="checkbox" name="%(value)s" id="%(value)s" value="true">
    <label for="%(value)s">%(name)s</label>
    <code>%(docs)s</code>
  </p>
'''

PERSONIFICATION_TEMPLATE = '''
  <p class="radio-line personification" style="margin: 0; padding: 0">
    <input %(checked)s type="radio" name="whom" id="%(value)s" value="%(value)s">
    <label for="%(value)s">%(name)s</label>
  </p>
'''

FORM = '''
  <section>
    <form>
      <h3>Construct a sentence</h3>
      <p>
        <label>Subject</label>
        <input
          required
          type="text"
          placeholder="Ali, Kitap, Yol"
          name="subject"
          value="%(subject)s"
        />
      </p>
      <div>
        <label>Case</label>
        %(cases)s
      </div>
      <p>
        <label>Predicate</label>
        <input
          required
          type="text"
          placeholder="Gel, Öl, Git"
          name="predicate"
          value="%(predicate)s"
        />
      </p>
      <div>
        <label>Copula</label>
        %(copulas)s
      </div>
      <div>
        <br />
        <label>Whom?</label>
        %(whom)s
      </div>
      <p>
        <input type="submit" />
      </p>
    </form>
  </section>
'''

RESULT = '''
<section id="result">
  <h3>Result</h3>
  <p>
    %(content)s
  </p>
</section>
'''

VISUALIZATION = '''
<span class="visualization">
  <i style="color: %s">%s</i> <strong>%s</strong>
</span>
'''

def colorize(text):
  return COLOR_MAP.get(text, 'black')

def render_case(case):
  doc = case.__doc__.splitlines()

  [name] = filter(
    lambda x: x.strip().startswith('##'),
    doc
  )

  docs = NOTHING.join(
    filter(
      lambda x: not x.strip().startswith('##'),
      doc
    )
  )

  try:
    description, examples = docs.split('✎︎')
  except ValueError:
    description = docs
    examples = NOTHING

  docs = description

  return CASE_TEMPLATE % {
    'name': name.replace('##', NOTHING),
    'docs': NOTHING.join(docs),
    'value': case.__name__,
    'checked': (
      'checked' if (
           (request.args.get('case') == case.__name__)
        or (case.__name__ == 'nominative' and not request.args.get('case'))
      ) else NOTHING
    ),
  }


def render_copula(copula):
  [doc, *tests] = copula.__doc__.split('✎︎ tests')
  [name] = filter(
    lambda x: x.strip().startswith('###'),
    doc.splitlines()
  )

  docs = BREAK_LINE.join(
    filter(
      lambda x: bool(x.strip()),
      map(
        lambda x: (
          x.replace('```python', NOTHING)
          .replace('```', NOTHING)
        ),
        filter(
          lambda x: not x.strip().startswith('###'),
          doc.splitlines()
        )
      )
    )
  )

  return COPULA_TEMPLATE % {
    'name': name.replace('#', NOTHING),
    'docs': docs,
    'value': copula.__name__,
    'checked': (
      'checked' if (
           (copula.__name__ in request.args)
        or (copula.__name__ == 'zero' and not request.args.get('copula'))
      ) else NOTHING
    ),
  }


def render_whom(personification):
  label = {
    first_person_singular: 'Singular First Person (Ben)',
    second_person_singular: 'Singular Second Person (Sen)', 
    third_person_singular: 'Singular Third Person (O)',
    first_person_plural: 'Plural First Person (Biz)',
    second_person_plural: 'Plural Second Person (Siz)', 
    third_person_plural: 'Plural Third Person (Onlar)',
  }.get(personification,)

  return PERSONIFICATION_TEMPLATE % {
    'name': label,
    'value': personification.__name__,
    'checked': (
      'checked' if (
           (request.args.get('whom') == personification.__name__)
        or (personification.__name__ == 'first_person_singular' and not request.args.get('whom'))
      ) else NOTHING
    ),
  }


def render_result(args):
  strip_tags = lambda text: (
    text
      .replace('<', NOTHING)
      .replace('>', NOTHING)
  )

  copulas = [
    copula
    for copula in COPULAS
    if copula.__name__ in args
  ]

  subject = strip_tags(args.get('subject'))
  predicate = strip_tags(args.get('predicate'))
  subject_case = strip_tags(args.get('case'))

  try:
    [case_processor] = filter(
      lambda case: case.__name__ == subject_case,
      CASES
    )
  except ValueError:
    case_processor = lambda identity: identity

  parts = [
    ('subject', subject, 'black'),
    (subject_case, case_processor(subject)[len(subject):], colorize(case_processor)),
    ('predicate', predicate, 'black'),
  ]

  rendered = predicate

  for copula in copulas:
    if 'whom' in copula.__code__.co_varnames:
      kwargs = {
        'whom': {
          'first_person_singular': Person.FIRST,
          'second_person_singular': Person.SECOND,
          'third_person_singular': Person.THIRD,
          'first_person_plural': Person.FIRST,
          'second_person_plural': Person.SECOND,
          'third_person_plural': Person.THIRD,
          }.get(args.get('whom')),
        'is_plural': args.get('whom') in (
          'first_person_plural',
          'second_person_plural',
          'third_person_plural',
        )
      }
    else:
      kwargs = {}

    before_render = len(rendered)
    rendered = copula(rendered, **kwargs)

    parts.append((
      copula.__name__,
      rendered[before_render:],
      colorize(copula)
    ))

  return RESULT % {
    'content': NOTHING.join(
      VISUALIZATION % (color, name, value) for (name, value, color) in parts
    )
  }


@app.route('/')
def index():
  cases = BREAK_LINE.join(map(render_case, CASES))
  copulas = BREAK_LINE.join(map(render_copula, COPULAS))
  whom = NOTHING.join(map(render_whom, WHOM))

  form = FORM % {
    'cases': cases,
    'copulas': copulas,
    'whom': whom,
    'subject': request.args.get('subject', NOTHING).replace('"', NOTHING),
    'predicate': request.args.get('predicate', NOTHING).replace('"', NOTHING),
  }

  if ('subject' in request.args or 'predicate' in request.args):
    result = render_result(request.args)
  else:
    result = NOTHING

  return(BASE_TEMPLATE % {
    'content': NOTHING.join(filter(bool, [result, form]))
  })

if __name__ == '__main__':
    app.run(debug=True)

