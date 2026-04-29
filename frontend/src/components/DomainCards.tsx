"use client";
import Link from "next/link";
import { motion } from "framer-motion";
import { DOMAINS } from "@/lib/constants";

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15 } },
};

const card = {
  hidden: { opacity: 0, y: 40 },
  show:   { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.22, 1, 0.36, 1] } },
};

export default function DomainCards() {
  return (
    <section id="domains" className="relative z-10 py-24 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Section header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="text-center mb-16"
        >
          <p className="text-xs tracking-[0.4em] text-gold-500 uppercase mb-3">解析領域</p>
          <h2 className="font-serif text-3xl md:text-4xl font-bold text-parchment">
            四大命理面向
          </h2>
          <div className="divider-gold w-32 mx-auto mt-6" />
        </motion.div>

        {/* Cards grid */}
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-50px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5"
        >
          {DOMAINS.map((domain) => (
            <motion.div key={domain.id} variants={card}>
              <Link href={`/analyze?domain=${domain.id}`} className="block h-full group">
                <div
                  className="card-gold h-full p-6 rounded-2xl cursor-pointer
                    transition-all duration-500 group-hover:-translate-y-2
                    group-hover:shadow-gold-md relative overflow-hidden"
                >
                  {/* Background gradient blob */}
                  <div
                    className={`absolute inset-0 bg-gradient-to-br ${domain.color} rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
                  />

                  {/* Icon */}
                  <div
                    className="relative text-3xl text-gold-500 mb-4 transition-all
                      duration-500 group-hover:text-gold-300 group-hover:scale-110
                      group-hover:drop-shadow-[0_0_12px_rgba(201,168,76,0.8)]"
                  >
                    {domain.icon}
                  </div>

                  {/* Title */}
                  <h3 className="relative font-serif text-xl font-semibold text-parchment mb-2">
                    {domain.name}
                  </h3>

                  {/* Description */}
                  <p className="relative text-sm text-parchment-muted leading-relaxed">
                    {domain.description}
                  </p>

                  {/* Bottom CTA */}
                  <p className="relative mt-4 text-xs text-gold-600 tracking-wider opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    點擊推算 →
                  </p>
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>

        {/* Bottom feature row */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.5 }}
          className="mt-20 grid grid-cols-3 gap-8 text-center"
        >
          {[
            { value: "AI", label: "Multi-Agent 推理" },
            { value: "RAG", label: "專業知識庫支撐" },
            { value: "即時", label: "動態星象資料" },
          ].map((f) => (
            <div key={f.value} className="flex flex-col items-center gap-2">
              <span className="font-serif text-2xl text-gold-gradient font-bold">{f.value}</span>
              <span className="text-xs text-parchment-muted tracking-wider">{f.label}</span>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
