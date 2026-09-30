/* Contributor Node Component */
import React, { useMemo } from 'react';
import { Handle, Position } from '@xyflow/react';
import CustomTooltipContent from './CustomTooltipContent';

const ContributorNode = ({ data }) => {
  const { issueCount, commitCount } = useMemo(() => {
    let issues = 0;
    let commits = 0;
    if (data.works) {
      data.works.forEach(work => {
        issues += work.issues?.length || 0;
        commits += work.commits?.length || 0;
      });
    }
    return { issueCount: issues, commitCount: commits };
  }, [data.works]);

  const tooltipData = {
    id: data.id,
    name: data.username,
    url: data.url,
    avatar: data.avatar_url,
    summary: data.summary,
    type: 'contributor',
    issueCount,
    commitCount
  };

  const nodeWidth = 180;
  const nodeHeight = 60;

  return (
    // The main div remains the group parent
    <div
      className="contributor-node group relative bg-white/95 dark:bg-slate-800/95 border border-emerald-200/60 dark:border-emerald-900/40 rounded-xl shadow-sm hover:shadow-md transition-all duration-300 flex items-center h-full backdrop-blur-md"
      style={{ width: nodeWidth, height: nodeHeight }}
    >
       {/* Node Content Wrapper */}
       <div className="p-2.5 flex items-center flex-grow">
          {/* Handles without specific IDs */}
          <Handle type="target" position={Position.Left} className="!w-1 !h-full !rounded-none !bg-transparent !border-none" />
          <Handle type="source" position={Position.Top} className="!w-2.5 !h-2.5 !bg-emerald-500 !rounded-full !border-2 !border-white" />

          {data.avatar_url ? (
            <img
              src={data.avatar_url}
              alt={data.username}
              className="w-9 h-9 rounded-full border-2 border-emerald-500/30 shadow-sm flex-shrink-0 object-cover"
            />
          ) : (
            <div className="w-9 h-9 rounded-full bg-emerald-100 dark:bg-emerald-900/40 text-emerald-800 dark:text-emerald-300 font-bold text-sm flex items-center justify-center flex-shrink-0">
              {data.username ? data.username.substring(0, 1).toUpperCase() : '?'}
            </div>
          )}
          <div className="ml-2.5 flex-grow min-w-0">
            <h4 className="text-xs font-semibold text-gray-900 dark:text-white truncate" title={data.username}>{data.username}</h4>
            <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Engineer</span>
          </div>
       </div>

      {/* Tooltip: Sibling to content wrapper, still inside the 'group' div */}
      {/* pointer-events-none initially, group-hover:pointer-events-auto allows interaction only when visible */}
      <div
        className="absolute z-50 left-full top-1/2 transform -translate-y-1/2 ml-3 w-72
                   opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto
                   transition-opacity duration-200 delay-300 group-hover:delay-300"
      >
        <div className="bg-white dark:bg-slate-800 shadow-xl rounded-lg p-4 border border-gray-200 dark:border-slate-700">
          <CustomTooltipContent content={tooltipData} />
        </div>
      </div>
    </div>
  );
};

export default ContributorNode;