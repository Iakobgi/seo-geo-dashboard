import AgentPanel from "../components/AgentPanel";
import { PageHeading } from "../components/UI";
export default function Agent() {
  return (
    <div className="space-y-6">
      <PageHeading
        title="Give your next idea a head start."
        description="Generate an optimization plan and draft content, ready for your review."
        eyebrow="AI WORKSPACE"
      />
      <AgentPanel />
      <div className="panel text-xs text-gray-500">
        Review generated content before publishing it on your website. Scores
        reflect the audited page; run another audit after applying changes to
        measure the result.
      </div>
    </div>
  );
}
