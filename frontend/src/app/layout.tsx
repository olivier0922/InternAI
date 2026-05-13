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
    <html lang="en" className="dark">
      <body className={`${inter.variable} antialiased`}>
        {children}
        <Toaster theme="dark" position="bottom-right" />
      </body>
    </html>
  );
}
