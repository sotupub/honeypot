'use client';

interface Attack {
  timestamp: string;
  ip_address: string;
  attack_type: string;
  payload?: string;
  status: string;
}

interface AttackTableProps {
  attacks?: Attack[];
}

const AttackTable = ({ attacks = [] }: AttackTableProps) => {
  return (
    <div className="glass-card">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-200 to-white">
          Recent Attacks
        </h2>
        <span className="glass px-3 py-1 rounded-full text-sm text-blue-100">
          {attacks.length} attacks detected
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-blue-200/10">
              <th className="text-left py-3 px-4 text-blue-100 text-sm font-medium">
                Time
              </th>
              <th className="text-left py-3 px-4 text-blue-100 text-sm font-medium">
                IP Address
              </th>
              <th className="text-left py-3 px-4 text-blue-100 text-sm font-medium">
                Attack Type
              </th>
              <th className="text-left py-3 px-4 text-blue-100 text-sm font-medium">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-blue-200/10">
            {attacks.length > 0 ? (
              attacks.map((attack, index) => (
                <tr key={index} className="group hover:bg-white/5 transition-colors">
                  <td className="py-3 px-4 text-sm text-blue-100">
                    {new Date(attack.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-sm font-medium text-white group-hover:text-blue-200 transition-colors">
                      {attack.ip_address}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-blue-100">
                    {attack.attack_type}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      attack.status === 'blocked' 
                        ? 'bg-red-500/20 text-red-300'
                        : attack.status === 'detected'
                        ? 'bg-yellow-500/20 text-yellow-300'
                        : 'bg-green-500/20 text-green-300'
                    }`}>
                      {attack.status}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="py-4 text-center text-blue-100/60">
                  No attacks detected yet
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AttackTable;
