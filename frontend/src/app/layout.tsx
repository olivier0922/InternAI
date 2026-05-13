import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "InternAI — AI-Powered Internship Discovery",
  description:
    "Find your dream software engineering internship with AI-powered job matching, real-time job aggregation, and smart resume analysis.",
  keywords: [
    "internship",
    "software engineering",
    "job search",
    "AI",
    "resume",
    "career",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="w-full overflow-x-hidden bg-background text-foreground">
      <body className={`${inter.variable} antialiased w-full overflow-x-hidden min-h-screen flex flex-col`}>
        {children}
        <Toaster theme="light" position="bottom-right" />
      </body>
    </html>
  );
}
