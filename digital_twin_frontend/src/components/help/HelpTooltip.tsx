import {
  CircleHelp,
} from "lucide-react";

interface HelpTooltipProps {
  term: string;
  text: string;
}

export function HelpTooltip({
  term,
  text,
}: HelpTooltipProps) {

  return (
    <span
      className="help-tooltip"
      tabIndex={0}
      aria-label={`${term}: ${text}`}
    >
      <CircleHelp
        size={14}
        aria-hidden="true"
      />

      <span
        className="help-tooltip-content"
        role="tooltip"
      >
        <strong>
          {term}
        </strong>

        <span>
          {text}
        </span>
      </span>
    </span>
  );
}
