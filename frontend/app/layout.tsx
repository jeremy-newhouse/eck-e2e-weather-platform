import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "@/providers";
import NavBar from "@/components/layout/NavBar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Weather Platform",
  description: "Real-time weather data with AI assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <NavBar />
          <main className="container mx-auto px-4 py-8">{children}</main>
        </Providers>
      </body>
    </html>
  );
}
