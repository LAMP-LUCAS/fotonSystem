"""
InfoPatternResolver — Value Object for configurable INFO file naming.

Resolves template strings with {placeholders} into filenames,
glob patterns, regex extraction patterns, and markdown headers.

Placeholders available:
  Client:   {codCliente}, {nomeCliente}, {aliasCliente}
  Service:  {codServico}, {aliasServico}, {aliasCliente}
  Version:  {versao}, {revisao}
  System:   {data}, {dataISO}, {ano}, {mes}, {timestamp}, {extensao}
"""

import re


_PLACEHOLDER_RE = re.compile(r'\{(\w+)\}')
_EXTENSION_RE = re.compile(r'(\.\w+$)|(\.\{extensao\}$)')


class InfoPatternResolver:
    """Resolves named placeholders in a filename pattern.

    Usage:
        resolver = InfoPatternResolver("INFO-CLIENTE-{codCliente}_{versao}_R{revisao}.md")
        name = resolver.resolve(codCliente="JOS01", versao="00", revisao="01")
        # → "INFO-CLIENTE-JOS01_00_R01.md"
    """

    def __init__(self, pattern: str):
        """Initialize with a pattern string containing {placeholders}.

        Raises ValueError if pattern is empty or has no file extension.
        """
        if not pattern or not pattern.strip():
            raise ValueError("Pattern cannot be empty")

        if not _EXTENSION_RE.search(pattern):
            raise ValueError(
                f"Pattern must include a file extension (e.g. .md): '{pattern}'"
            )

        self._pattern = pattern.strip()
        self._placeholders = set(
            _PLACEHOLDER_RE.findall(self._pattern)
        )

    @property
    def pattern(self) -> str:
        """The raw pattern string."""
        return self._pattern

    @property
    def placeholders(self) -> set:
        """Set of placeholder names found in the pattern."""
        return set(self._placeholders)

    def resolve(self, **kwargs) -> str:
        """Substitute placeholders with values and return the final filename.

        Raises ValueError if any placeholder in the pattern has no
        corresponding keyword argument.
        """
        missing = self._placeholders - set(kwargs.keys())
        if missing:
            raise ValueError(
                f"Missing values for placeholders: {', '.join(sorted(missing))}"
            )
        result = self._pattern
        for key, value in kwargs.items():
            if key in self._placeholders:
                result = result.replace(f'{{{key}}}', str(value))
        return result

    def to_glob(self) -> str:
        """Convert pattern to a glob-compatible string for file search.

        Each {placeholder} is replaced with '*' to match any value.
        Adjacent placeholders produce a single '*' (collapsed) so
        glob patterns remain valid.
        """
        result = _PLACEHOLDER_RE.sub('*', self._pattern)
        # Collapse consecutive asterisks (adjacent placeholders)
        result = re.sub(r'\*+', '*', result)
        return result

    def to_header(self) -> str:
        """Return a markdown header (##) with the raw pattern.

        Placeholders remain as literals for use as section headers.
        """
        return f"## {self._pattern}"

    def extract(self, filename: str) -> dict:
        """Extract placeholder values from a filename string.

        This is the inverse operation of resolve().

        Returns a dict mapping placeholder names to their extracted values.
        Returns an empty dict if the filename doesn't match the pattern.

        Note: adjacent placeholders (no delimiter between them) use a
        greedy-first-then-backtrack heuristic which may not always produce
        intuitive results.
        """
        tokens = re.split(r'(\{(\w+)\})', self._pattern)
        # tokens format: ['lit', '{ph}', 'ph_name', 'lit', ...]
        ph_names = []
        for i, t in enumerate(tokens):
            if re.match(r'^\{\w+\}$', t):
                ph_names.append(tokens[i + 1])

        ph_idx = 0
        regex_chars = []
        i = 0
        while i < len(tokens):
            if re.match(r'^\{\w+\}$', tokens[i]):
                name = tokens[i + 1]
                is_last = (ph_idx == len(ph_names) - 1)
                # Last group uses greedy .+ (consumes remaining after others);
                # earlier groups use non-greedy .+? (minimal match so later
                # groups have room). This is deterministic and predictable:
                # each non-last group captures the shortest possible string.
                if is_last:
                    regex_chars.append(f'(?P<{name}>.+)')
                else:
                    regex_chars.append(f'(?P<{name}>.+?)')
                i += 2
                ph_idx += 1
            else:
                if tokens[i]:
                    regex_chars.append(re.escape(tokens[i]))
                i += 1

        regex = '^' + ''.join(regex_chars) + '$'
        m = re.match(regex, filename)
        if not m:
            return {}
        return {name: m.group(name) for name in ph_names}

    @classmethod
    def validate(cls, pattern: str) -> bool:
        """Check if a pattern string is syntactically valid.

        Returns True if the pattern has content and a file extension.
        """
        if not pattern or not pattern.strip():
            return False
        return bool(_EXTENSION_RE.search(pattern))

    def __repr__(self) -> str:
        return f"InfoPatternResolver('{self._pattern}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, InfoPatternResolver):
            return NotImplemented
        return self._pattern == other._pattern

    def __hash__(self) -> int:
        return hash(self._pattern)
