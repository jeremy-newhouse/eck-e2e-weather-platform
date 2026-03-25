import Link from "next/link";

export default function NavBar() {
  return (
    <nav className="bg-blue-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold">
          Weather Platform
        </Link>
        <div className="flex gap-6">
          <Link href="/" className="hover:text-blue-200 transition-colors">
            Home
          </Link>
          <Link
            href="/dashboard"
            className="hover:text-blue-200 transition-colors"
          >
            Dashboard
          </Link>
          <Link href="/chat" className="hover:text-blue-200 transition-colors">
            Chat
          </Link>
        </div>
      </div>
    </nav>
  );
}
