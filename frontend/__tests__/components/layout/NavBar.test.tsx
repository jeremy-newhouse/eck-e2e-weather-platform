import { render, screen } from "@testing-library/react";
import NavBar from "@/components/layout/NavBar";

// Mock next/link
jest.mock("next/link", () => {
  const MockLink = ({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) => <a href={href}>{children}</a>;
  MockLink.displayName = "MockLink";
  return MockLink;
});

describe("NavBar", () => {
  it("renders the brand name", () => {
    render(<NavBar />);
    expect(screen.getByText("Weather Platform")).toBeInTheDocument();
  });

  it("renders Home link with correct href", () => {
    render(<NavBar />);
    const homeLinks = screen.getAllByRole("link", { name: /home/i });
    expect(homeLinks.length).toBeGreaterThan(0);
    expect(homeLinks[0]).toHaveAttribute("href", "/");
  });

  it("renders Dashboard link with correct href", () => {
    render(<NavBar />);
    const dashboardLink = screen.getByRole("link", { name: /dashboard/i });
    expect(dashboardLink).toHaveAttribute("href", "/dashboard");
  });

  it("renders Chat link with correct href", () => {
    render(<NavBar />);
    const chatLink = screen.getByRole("link", { name: /chat/i });
    expect(chatLink).toHaveAttribute("href", "/chat");
  });

  it("renders a nav element", () => {
    render(<NavBar />);
    expect(screen.getByRole("navigation")).toBeInTheDocument();
  });
});
