import { ExternalLink } from "lucide-react";
import { AUTHOR, PORTFOLIO_URL, RELATED_PROJECTS, REPO_URL } from "../config/links";

function FooterLink({ href, children }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 text-gray-400 hover:text-bronze transition-colors"
    >
      {children}
      <ExternalLink size={12} />
    </a>
  );
}

export default function Footer() {
  return (
    <footer className="max-w-5xl w-full mx-auto mt-16 pt-8 border-t border-bronze/20 text-sm">
      <div className="grid gap-8 md:grid-cols-2">
        <div>
          <p className="text-white font-semibold mb-3">Built by {AUTHOR.name}</p>
          <div className="flex flex-col items-start gap-2">
            {PORTFOLIO_URL && <FooterLink href={PORTFOLIO_URL}>Portfolio</FooterLink>}
            <FooterLink href={AUTHOR.github}>GitHub profile</FooterLink>
            <FooterLink href={REPO_URL}>Source code of BannerHound</FooterLink>
          </div>
        </div>

        <div>
          <p className="text-white font-semibold mb-3">More projects</p>
          <ul className="space-y-3">
            {RELATED_PROJECTS.map((project) => (
              <li key={project.name}>
                <FooterLink href={project.url}>{project.name}</FooterLink>
                <p className="text-gray-500 text-xs mt-0.5">{project.description}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <p className="text-center text-xs text-gray-600 mt-8">
        For authorized network auditing and educational use only. Only scan
        networks you own or have explicit permission to test.
      </p>
    </footer>
  );
}