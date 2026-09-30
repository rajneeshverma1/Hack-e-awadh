import React from 'react';
import { Handle, Position } from '@xyflow/react';
import CustomTooltipContent from './CustomTooltipContent';

const RepositoryNode = ({ data }) => {
  const nodeWidth = 220;
  const nodeHeight = 150;

  return (
    // The main div remains the group parent
    <div
      className="repository-node group relative bg-white/95 dark:bg-slate-800/95 border border-gray-200/80 dark:border-slate-700/80 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 flex flex-col h-full text-sm backdrop-blur-md"
      style={{ width: nodeWidth, height: nodeHeight }}
    >
      {/* Node Content Wrapper */}
      <div className="p-3.5 flex flex-col flex-grow">
        {/* Handles with IDs */}
        <Handle type="target" position={Position.Bottom} className="!w-2.5 !h-2.5 !bg-indigo-500 !rounded-full !border-2 !border-white" />

        <h3 className="text-sm font-bold text-gray-900 dark:text-white truncate mb-1" title={data.name}>{data.name}</h3>
        <p className="text-xs text-gray-600 dark:text-gray-300 flex-grow overflow-hidden line-clamp-3 mb-2 leading-relaxed">
          {data.summary || 'No description available.'}
        </p>
        <div className="flex justify-between items-center mt-auto pt-1.5 border-t border-gray-100 dark:border-slate-700/80">
          <span className="text-[10px] uppercase font-semibold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 px-2 py-0.5 rounded-full">Repository</span>
        </div>
      </div>
    </div>
  );
};

export default RepositoryNode;